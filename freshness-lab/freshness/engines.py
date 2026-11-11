"""Engine adapters. Each returns a normalised ProbeResult.

Credentials are read from the environment (OPENAI_API_KEY, ANTHROPIC_API_KEY,
PERPLEXITY_API_KEY, GEMINI_API_KEY). In a Claude Code cloud session the network
proxy can inject the real key, so a placeholder value is enough there.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field, asdict

import requests

TIMEOUT = 120


@dataclass
class ProbeResult:
    engine: str
    model: str
    text: str = ""
    cited_urls: list[str] = field(default_factory=list)
    search_queries: list[str] = field(default_factory=list)
    error: str | None = None
    latency_s: float = 0.0
    raw_stop: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _key(name: str) -> str:
    return os.environ.get(name, "placeholder-injected-by-proxy")


# --------------------------------------------------------------------------- OpenAI
def probe_openai(prompt: str, model: str) -> ProbeResult:
    """OpenAI Responses API with the hosted web_search tool."""
    t0 = time.time()
    r = ProbeResult(engine="chatgpt", model=model)
    try:
        resp = requests.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {_key('OPENAI_API_KEY')}", "Content-Type": "application/json"},
            json={"model": model, "input": prompt, "tools": [{"type": "web_search"}]},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("output", []):
            if item.get("type") == "web_search_call":
                q = (item.get("action") or {}).get("query")
                if q:
                    r.search_queries.append(q)
            if item.get("type") == "message":
                for part in item.get("content", []):
                    if part.get("type") == "output_text":
                        r.text += part.get("text", "")
                        for a in part.get("annotations", []) or []:
                            if a.get("type") == "url_citation" and a.get("url"):
                                r.cited_urls.append(a["url"])
        r.raw_stop = data.get("status")
    except Exception as e:  # noqa: BLE001 - record and continue; one engine failing must not stop the run
        r.error = f"{type(e).__name__}: {e}"[:500]
    r.latency_s = round(time.time() - t0, 2)
    return r


# --------------------------------------------------------------------------- Perplexity
def probe_perplexity(prompt: str, model: str) -> ProbeResult:
    t0 = time.time()
    r = ProbeResult(engine="perplexity", model=model)
    try:
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {_key('PERPLEXITY_API_KEY')}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "user", "content": prompt}]},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        r.text = data["choices"][0]["message"]["content"]
        urls = list(data.get("citations") or [])
        urls += [s.get("url") for s in (data.get("search_results") or []) if s.get("url")]
        r.cited_urls = list(dict.fromkeys(urls))
        r.raw_stop = data["choices"][0].get("finish_reason")
    except Exception as e:  # noqa: BLE001
        r.error = f"{type(e).__name__}: {e}"[:500]
    r.latency_s = round(time.time() - t0, 2)
    return r


# --------------------------------------------------------------------------- Gemini
def probe_gemini(prompt: str, model: str) -> ProbeResult:
    """Gemini with Google Search grounding. Grounding chunk URIs are Google redirect
    links; the chunk title carries the source domain, which we keep alongside."""
    t0 = time.time()
    r = ProbeResult(engine="gemini", model=model)
    try:
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={"x-goog-api-key": _key("GEMINI_API_KEY"), "Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}], "tools": [{"google_search": {}}]},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        cand = (data.get("candidates") or [{}])[0]
        r.text = "".join(p.get("text", "") for p in (cand.get("content") or {}).get("parts", []))
        gm = cand.get("groundingMetadata") or {}
        r.search_queries = list(gm.get("webSearchQueries") or [])
        for ch in gm.get("groundingChunks") or []:
            web = ch.get("web") or {}
            if web.get("uri"):
                r.cited_urls.append(web["uri"] + (f"#title={web['title']}" if web.get("title") else ""))
        r.raw_stop = cand.get("finishReason")
    except Exception as e:  # noqa: BLE001
        r.error = f"{type(e).__name__}: {e}"[:500]
    r.latency_s = round(time.time() - t0, 2)
    return r


# --------------------------------------------------------------------------- Claude
def probe_claude(prompt: str, model: str, max_continuations: int = 3) -> ProbeResult:
    """Claude via the official Anthropic SDK with the server-side web search tool.

    - web_search_20260209 (dynamic filtering) on current models
    - server-side refusal fallbacks enabled (fallbacks="default")
    - effort set explicitly to "low": this is a short factual lookup
    - pause_turn is resumed by re-sending the assistant content (no "continue" message)
    """
    import anthropic

    t0 = time.time()
    r = ProbeResult(engine="claude", model=model)
    try:
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY") or "placeholder-injected-by-proxy")
        messages = [{"role": "user", "content": prompt}]
        params = dict(
            model=model,
            max_tokens=16000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": "low"},
            tools=[{"type": "web_search_20260209", "name": "web_search"}],
        )
        resp = client.beta.messages.create(messages=messages, **params)
        n = 0
        while resp.stop_reason == "pause_turn" and n < max_continuations:
            messages = [{"role": "user", "content": prompt}, {"role": "assistant", "content": resp.content}]
            resp = client.beta.messages.create(messages=messages, **params)
            n += 1
        r.raw_stop = resp.stop_reason
        if resp.stop_reason == "refusal":
            r.error = "refusal"
        for block in resp.content:
            btype = getattr(block, "type", None)
            if btype == "text":
                r.text += block.text
                for c in getattr(block, "citations", None) or []:
                    url = getattr(c, "url", None)
                    if url:
                        r.cited_urls.append(url)
            elif btype == "server_tool_use" and getattr(block, "name", "") == "web_search":
                q = (getattr(block, "input", None) or {}).get("query")
                if q:
                    r.search_queries.append(q)
            elif btype == "web_search_tool_result":
                content = getattr(block, "content", None)
                if isinstance(content, list):  # an error result is an object, not a list
                    for res in content:
                        url = getattr(res, "url", None)
                        if url:
                            r.cited_urls.append(url)
        r.cited_urls = list(dict.fromkeys(r.cited_urls))
    except anthropic.RateLimitError as e:
        r.error = f"rate_limited: {e}"[:500]
    except anthropic.APIStatusError as e:
        r.error = f"api_status_{e.status_code}: {e}"[:500]
    except anthropic.APIConnectionError as e:
        r.error = f"connection: {e}"[:500]
    r.latency_s = round(time.time() - t0, 2)
    return r


ADAPTERS = {
    "chatgpt": probe_openai,
    "perplexity": probe_perplexity,
    "gemini": probe_gemini,
    "claude": probe_claude,
}
