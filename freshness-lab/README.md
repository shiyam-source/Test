# Slate Freshness Lab

**Question:** when you change a fact on your page, how long until ChatGPT, Perplexity, Claude and Gemini give the new answer, and does that line up with when their crawlers fetched the page?

**Hook for the post:** "We changed a price on Monday. ChatGPT knew by ___. Claude by ___."

## Design

| Piece | What it is |
|---|---|
| **Canaries** | True facts on pages we control that change on a known date (a price, the SlateIndex brand count, a stat in a ranking blog post, a changelog entry, a brand-new URL). Never false information. |
| **Arms** | `ping`: on change day, submit via IndexNow (Bing, which ChatGPT search draws on), request indexing in Google Search Console, update the sitemap `lastmod`. `no-ping`: change only. `control`: an unchanged page probed the same way, to measure false positives. |
| **Probes** | For every canary: 3 prompt phrasings (brand question, category question, URL-explicit question) × 4 engines × 2 repetitions, via each engine's API with web search on. |
| **Crawler logs** | Server or CDN logs filtered to AI crawler user agents: `OAI-SearchBot`, `ChatGPT-User`, `GPTBot`, `PerplexityBot`, `Perplexity-User`, `Claude-SearchBot`, `Claude-User`, `ClaudeBot`, `Googlebot`, `bingbot` and more. |
| **Schedule** | Baseline 3 days before the change (proves each engine can see the page at all), then twice daily for week 1 and daily until day 28. |

### Metrics, per canary × engine

- **Crawler fetch**: hours from the edit to the first fetch of that URL by the engine's crawler.
- **First fresh answer**: hours to the first answer containing the new value.
- **Stable**: hours until every later probe round has at least 80% of value-stating answers on the new value.
- **Last stale answer**: the last time the old value was still quoted.
- **Baseline sees page**: share of pre-change answers that quote the old value or cite the page. If this is low, that engine's freshness can't be measured on this page.
- **No-answer rate**: answers that state no value at all, reported separately.

### Known limits (state them in the post)

- **API, not the consumer apps.** UI retrieval differs. A UI spot-check on day 1, 3 and 7 is recommended.
- **One site.** Domain authority and crawl budget affect latency, so results describe slatehq.com / slateindex.ai, not the web.
- **Google AI Overviews / AI Mode aren't probed in v1.** They need a SERP provider (adapter slot left open).
- **User-agent matching can be spoofed.** Verify crawler IPs against the vendors' published ranges before publishing.

## Layout

```
freshness/engines.py   adapters: OpenAI Responses + web_search, Perplexity sonar, Gemini + Google Search grounding, Claude (Anthropic SDK + web_search_20260209)
freshness/detect.py    new / both / old / neither classification, canary-URL citation check
freshness/probe.py     one probe round -> data/probes.jsonl   (--dry-run uses simulated engines)
freshness/logs.py      access / Cloudflare / CSV logs -> data/fetches.jsonl
freshness/report.py    data -> data/summary.json + reports/freshness-report.html
freshness/mock.py      simulated engines for dry runs (output watermarked SIMULATED)
config/canaries.example.yaml   template, copy to config/canaries.yaml
tests/test_pipeline.py end-to-end dry run, no network
run_daily.sh           one round + report
```

## Run

```bash
pip install -r requirements.txt
python3 tests/test_pipeline.py                     # dry run, no keys needed
cp config/canaries.example.yaml config/canaries.yaml   # fill in the TODOs
./run_daily.sh                                     # live round (needs API keys)
```

Credentials: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `PERPLEXITY_API_KEY`, `GEMINI_API_KEY`. In a Claude Code cloud session these are added through the environment's network secrets, so no key is ever written to a file.

Drop server or CDN log exports into `data/logs/` before each run, or have the CDN push them there.

## Cost (rough)

5 canaries × 3 prompts × 4 engines × 2 reps = 120 calls per round. About 40 rounds over 4 weeks ≈ 4,800 calls.

## Status

- [x] Harness, detection, log parsing, report, dry-run test
- [ ] Canary pages and change date agreed (marketing / web team)
- [ ] API credentials added
- [ ] Log access (Cloudflare Logpush or host logs) for slatehq.com and slateindex.ai
- [ ] Baseline rounds (3 days before the change)
- [ ] Change day: edits live, ping arm submitted
- [ ] 28 days of probes, then write-up
