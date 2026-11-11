"""Parse web server / CDN logs into AI-crawler fetch events.

Supported inputs:
  - combined log format (nginx, Apache)
  - Cloudflare Logpush JSON lines (EdgeStartTimestamp, ClientRequestUserAgent, ClientRequestPath, ClientIP)
  - CSV with header: timestamp,user_agent,path[,ip]

User-agent matching identifies the crawler family. IPs are recorded so they can
be checked against the vendors' published IP ranges before publishing results.

    python -m freshness.logs access.log [more logs...] --out data/fetches.jsonl
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone

# order matters: more specific tokens first
BOTS = [
    ("OAI-SearchBot", "openai", "search index"),
    ("ChatGPT-User", "openai", "live user fetch"),
    ("GPTBot", "openai", "training crawl"),
    ("Perplexity-User", "perplexity", "live user fetch"),
    ("PerplexityBot", "perplexity", "search index"),
    ("Claude-SearchBot", "anthropic", "search index"),
    ("Claude-User", "anthropic", "live user fetch"),
    ("ClaudeBot", "anthropic", "training crawl"),
    ("Google-CloudVertexBot", "google", "vertex fetch"),
    ("GoogleOther", "google", "other"),
    ("Googlebot", "google", "search index"),
    ("bingbot", "microsoft", "search index"),
    ("Applebot", "apple", "search index"),
    ("DuckAssistBot", "duckduckgo", "live user fetch"),
    ("MistralAI-User", "mistral", "live user fetch"),
    ("meta-externalagent", "meta", "training crawl"),
]
BOT_RE = [(re.compile(re.escape(tok), re.I), tok, vendor, role) for tok, vendor, role in BOTS]
COMBINED = re.compile(r'^(?P<ip>\S+) \S+ \S+ \[(?P<ts>[^\]]+)\] "(?:\S+) (?P<path>\S+)[^"]*" (?P<status>\d{3}) \S+ "[^"]*" "(?P<ua>[^"]*)"')


def identify(ua: str):
    for rx, tok, vendor, role in BOT_RE:
        if rx.search(ua or ""):
            return tok, vendor, role
    return None


def _ts_combined(s: str) -> str:
    return datetime.strptime(s, "%d/%b/%Y:%H:%M:%S %z").astimezone(timezone.utc).isoformat()


def _ts_any(v) -> str:
    if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()):
        x = float(v)
        x = x / 1e9 if x > 1e14 else x / 1e3 if x > 1e11 else x  # ns / ms / s
        return datetime.fromtimestamp(x, timezone.utc).isoformat()
    return datetime.fromisoformat(str(v).replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()


def parse_file(path: str):
    with open(path, newline="") as f:
        first = f.readline()
        f.seek(0)
        if first.startswith("{"):
            for line in f:
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                yield _ts_any(d.get("EdgeStartTimestamp") or d.get("timestamp")), d.get("ClientRequestUserAgent", ""), d.get("ClientRequestPath", ""), d.get("ClientIP"), d.get("EdgeResponseStatus")
        elif first.lower().startswith("timestamp,"):
            for row in csv.DictReader(f):
                yield _ts_any(row["timestamp"]), row.get("user_agent", ""), row.get("path", ""), row.get("ip"), row.get("status")
        else:
            for line in f:
                m = COMBINED.match(line)
                if m:
                    yield _ts_combined(m["ts"]), m["ua"], m["path"], m["ip"], m["status"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="+")
    ap.add_argument("--out", default="data/fetches.jsonl")
    a = ap.parse_args(argv)
    n = 0
    with open(a.out, "a") as out:
        for p in a.logs:
            for ts, ua, path, ip, status in parse_file(p):
                hit = identify(ua)
                if not hit:
                    continue
                tok, vendor, role = hit
                out.write(json.dumps({"ts": ts, "bot": tok, "vendor": vendor, "role": role, "path": path.split("?")[0], "ip": ip, "status": status}) + "\n")
                n += 1
    print(f"wrote {n} AI-crawler fetches to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
