"""Turn probe records (+ crawler fetches) into latency metrics and a chart.

    python -m freshness.report --config config/canaries.yaml

Writes data/summary.json and reports/freshness-report.html. Any simulated
record puts a SIMULATED watermark on the chart.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from urllib.parse import urlsplit

from . import config as cfgmod
from .detect import is_fresh

ENGINE_VENDOR = {"chatgpt": ["openai", "microsoft"], "perplexity": ["perplexity"], "claude": ["anthropic"], "gemini": ["google"]}
ENGINE_LABEL = {"chatgpt": "ChatGPT", "perplexity": "Perplexity", "claude": "Claude", "gemini": "Gemini"}
STABLE_SHARE = 0.8


def _read(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def _h(ts: str, t0: datetime) -> float:
    return round((datetime.fromisoformat(ts) - t0).total_seconds() / 3600, 1)


def summarise(cfg: dict, probes: list[dict], fetches: list[dict]) -> dict:
    out = {"simulated": any(p.get("simulated") for p in probes), "canaries": []}
    for c in cfg["canaries"]:
        t0 = datetime.fromisoformat(c["changed_at"])
        path = urlsplit(c["url"]).path.rstrip("/") or "/"
        cp = [p for p in probes if p["canary"] == c["id"]]
        entry = {"id": c["id"], "url": c["url"], "arm": c["arm"], "page_type": c.get("page_type"),
                 "changed_at": c["changed_at"], "engines": {}}
        for eng in sorted({p["engine"] for p in cp}):
            ep = [p for p in cp if p["engine"] == eng]
            pre = [p for p in ep if datetime.fromisoformat(p["ts"]) < t0 and p["status"] != "error"]
            post = sorted([p for p in ep if datetime.fromisoformat(p["ts"]) >= t0], key=lambda p: p["ts"])
            # fresh share counts only answers that state a value (new / both / old);
            # "neither" (no value given) is tracked separately as the no-answer rate
            rounds = defaultdict(list)
            for p in post:
                if p["status"] in ("new", "both", "old"):
                    rounds[p["ts"]].append(p)
            round_list = sorted(rounds.items())
            shares = [(ts, sum(is_fresh(p["status"]) for p in ps) / len(ps)) for ts, ps in round_list if ps]
            answered = [p for p in post if p["status"] != "error"]
            no_answer_rate = round(sum(p["status"] == "neither" for p in answered) / len(answered), 2) if answered else None
            first_fresh = next((p["ts"] for p in post if is_fresh(p["status"])), None)
            stable = None
            for i, (ts, _) in enumerate(shares):
                if all(s >= STABLE_SHARE for _, s in shares[i:]):
                    stable = ts
                    break
            stale = [p["ts"] for p in post if p["status"] == "old"]
            vendors = ENGINE_VENDOR.get(eng, [])
            fetch_after = sorted(f["ts"] for f in fetches if f["vendor"] in vendors and (f["path"].rstrip("/") or "/") == path and datetime.fromisoformat(f["ts"]) >= t0)
            entry["engines"][eng] = {
                "baseline_n": len(pre),
                "baseline_sees_page": round(sum(p["status"] == "old" or p["cites_canary_url"] for p in pre) / len(pre), 2) if pre else None,
                "post_n": len(post),
                "errors": sum(p["status"] == "error" for p in ep),
                "first_crawler_fetch_h": _h(fetch_after[0], t0) if fetch_after else None,
                "first_fresh_h": _h(first_fresh, t0) if first_fresh else None,
                "stable_fresh_h": _h(stable, t0) if stable else None,
                "last_stale_h": _h(stale[-1], t0) if stale else None,
                "latest_fresh_share": round(shares[-1][1], 2) if shares else None,
                "no_answer_rate": no_answer_rate,
                "rounds": [{"h": _h(ts, t0), "fresh_share": round(s, 2)} for ts, s in shares],
            }
        out["canaries"].append(entry)
    return out


def _fmt(h):
    if h is None:
        return "not yet"
    return f"{h:.0f} h" if h < 48 else f"{h / 24:.1f} days"


def render_html(summary: dict, logo_svg: str = "") -> str:
    OR = "#EE6216"
    blocks = []
    for c in summary["canaries"]:
        engines = c["engines"]
        if not engines:
            continue
        max_h = max([r["h"] for e in engines.values() for r in e["rounds"]] + [24])
        W, X0 = 640, 170
        sx = lambda h: X0 + max(h, 0) / max_h * W
        rows = ""
        order = sorted(engines, key=lambda e: (engines[e]["first_fresh_h"] is None, engines[e]["first_fresh_h"] or 0))
        for i, eng in enumerate(order):
            e = engines[eng]
            y = 40 + i * 74
            rows += f'<text x="0" y="{y + 6}" class="en">{ENGINE_LABEL.get(eng, eng)}</text>'
            rows += f'<line x1="{X0}" y1="{y}" x2="{X0 + W}" y2="{y}" stroke="#2A2A2A" stroke-width="10" stroke-linecap="round"/>'
            for r in e["rounds"]:  # fresh share per round as opacity dots
                rows += f'<circle cx="{sx(r["h"]):.1f}" cy="{y}" r="5" fill="{OR}" fill-opacity="{0.12 + 0.88 * r["fresh_share"]:.2f}"/>'
            if e["first_crawler_fetch_h"] is not None:
                x = sx(e["first_crawler_fetch_h"])
                rows += f'<path d="M{x:.1f} {y - 22} l7 7 l-7 7 l-7 -7 z" fill="#B9B5AF"/>'
            if e["first_fresh_h"] is not None:
                x = sx(e["first_fresh_h"])
                rows += f'<line x1="{x:.1f}" y1="{y - 16}" x2="{x:.1f}" y2="{y + 16}" stroke="{OR}" stroke-width="3"/>'
                rows += f'<text x="{x:.1f}" y="{y + 34}" class="lb" text-anchor="middle">{_fmt(e["first_fresh_h"])}</text>'
            else:
                rows += f'<text x="{X0 + W + 12}" y="{y + 5}" class="lb">not yet</text>'
        ticks = "".join(f'<line x1="{sx(h):.1f}" y1="10" x2="{sx(h):.1f}" y2="{40 + len(order) * 74 - 30}" stroke="#222"/><text x="{sx(h):.1f}" y="{40 + len(order) * 74 - 10}" class="ax" text-anchor="middle">{"change" if h == 0 else _fmt(h)}</text>' for h in sorted({0, round(max_h / 4), round(max_h / 2), round(3 * max_h / 4), round(max_h)}))
        svg = f'<svg width="900" height="{40 + len(order) * 74}" style="overflow:visible">{ticks}{rows}</svg>'
        table = "".join(
            f'<tr><td>{ENGINE_LABEL.get(k, k)}</td><td>{_fmt(v["first_crawler_fetch_h"])}</td><td><b>{_fmt(v["first_fresh_h"])}</b></td><td>{_fmt(v["stable_fresh_h"])}</td><td>{_fmt(v["last_stale_h"])}</td><td>{v["baseline_sees_page"] if v["baseline_sees_page"] is not None else "n/a"}</td></tr>'
            for k, v in engines.items())
        blocks.append(f'''<section><div class="k">CANARY · {html.escape(c["id"])} · {html.escape(c.get("page_type") or "")} · arm: {html.escape(c["arm"])}</div>
<div class="u">{html.escape(c["url"])} · changed {html.escape(c["changed_at"])}</div>{svg}
<div class="leg"><span><i class="d"></i>AI crawler first fetched the page</span><span><i class="b"></i>first answer with the new value</span><span><i class="o"></i>share of answers with the new value, per probe round</span></div>
<table><tr><th>engine</th><th>crawler fetch</th><th>first fresh answer</th><th>stable (≥80% fresh)</th><th>last stale answer</th><th>baseline: sees page</th></tr>{table}</table></section>''')
    wm = '<div class="wm">SIMULATED DATA · DRY RUN · NOT A FINDING</div>' if summary["simulated"] else ""
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>Freshness Lab report</title><style>
body{{background:#111;color:#F6F4F1;font-family:Inter,system-ui,sans-serif;margin:0;padding:40px 48px}}
h1{{font-size:40px;font-weight:500;letter-spacing:-1px;margin:8px 0 4px}} .e{{font-family:monospace;color:{OR};letter-spacing:2px;font-size:13px}}
section{{margin-top:36px;border-top:1px solid #2A2A2A;padding-top:20px}} .k{{font-family:monospace;color:{OR};font-size:12px;letter-spacing:1.5px}}
.u{{font-family:monospace;color:#8C8882;font-size:12px;margin:4px 0 14px}} svg .en{{fill:#F6F4F1;font-size:16px}} svg .lb{{fill:#F6F4F1;font-family:monospace;font-size:12px}} svg .ax{{fill:#8C8882;font-family:monospace;font-size:11px}}
.leg{{display:flex;gap:22px;font-family:monospace;font-size:12px;color:#B9B5AF;margin:8px 0 14px}} .leg i{{display:inline-block;width:10px;height:10px;margin-right:6px}}
.leg .d{{background:#B9B5AF;transform:rotate(45deg)}} .leg .b{{background:{OR};width:3px;height:14px}} .leg .o{{background:{OR};border-radius:50%;opacity:.6}}
table{{border-collapse:collapse;font-size:14px;margin-top:6px}} td,th{{padding:6px 14px 6px 0;text-align:left;border-bottom:1px solid #222}} th{{font-family:monospace;font-size:11px;color:#8C8882;font-weight:400}}
.wm{{position:fixed;top:14px;right:18px;font-family:monospace;font-size:13px;color:#111;background:#F5BACB;padding:6px 10px;border-radius:6px;letter-spacing:1px}}
</style></head><body>{wm}<div class="e">SLATE FRESHNESS LAB</div><h1>How long until AI notices a page change?</h1>
<div class="u">first fresh answer = first probe whose answer contains the new value · stable = every later round ≥80% fresh · probes via each engine's API with web search</div>
{"".join(blocks)}</body></html>'''


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/canaries.yaml")
    ap.add_argument("--probes", default="data/probes.jsonl")
    ap.add_argument("--fetches", default="data/fetches.jsonl")
    ap.add_argument("--summary", default="data/summary.json")
    ap.add_argument("--html", default="reports/freshness-report.html")
    a = ap.parse_args(argv)
    cfg = cfgmod.load(a.config)
    s = summarise(cfg, _read(a.probes), _read(a.fetches))
    os.makedirs(os.path.dirname(a.summary), exist_ok=True)
    os.makedirs(os.path.dirname(a.html), exist_ok=True)
    json.dump(s, open(a.summary, "w"), indent=2)
    open(a.html, "w").write(render_html(s))
    print(f"summary -> {a.summary}\nreport  -> {a.html}" + ("\n(SIMULATED data present)" if s["simulated"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
