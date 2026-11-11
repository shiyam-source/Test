"""End-to-end dry run: simulated probes over 3 weeks + synthetic crawler logs -> report.
Checks the pipeline produces sensible latencies. No network, no keys."""
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from freshness import config as cfgmod
from freshness.detect import classify, cites_canary, normalise_url
from freshness.logs import identify, main as logs_main
from freshness.mock import SIM_LATENCY_H
from freshness.probe import run_round
from freshness.report import summarise, render_html

HERE = os.path.dirname(os.path.abspath(__file__))


def test_classify_and_urls():
    assert classify("It costs $449 now", [r"\$449"], [r"\$499"]) == "new"
    assert classify("was $499, now $449", [r"\$449"], [r"\$499"]) == "both"
    assert classify("It costs $499", [r"\$449"], [r"\$499"]) == "old"
    assert classify("no idea", [r"\$449"], [r"\$499"]) == "neither"
    assert classify("x", [], [], error="timeout") == "error"
    assert normalise_url("https://www.SlateHQ.com/pricing/?utm=1#top") == "slatehq.com/pricing"
    assert cites_canary(["https://slatehq.com/pricing/"], "https://www.slatehq.com/pricing")


def test_bot_identification():
    assert identify("Mozilla/5.0 (compatible; OAI-SearchBot/1.0; +https://openai.com/searchbot)")[0] == "OAI-SearchBot"
    assert identify("Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ChatGPT-User/1.0)")[0] == "ChatGPT-User"
    assert identify("Mozilla/5.0 (compatible; Claude-User/1.0)")[1] == "anthropic"
    assert identify("Mozilla/5.0 (Windows NT 10.0) Chrome/120") is None


def test_end_to_end_dry_run():
    cfg = cfgmod.load(os.path.join(HERE, "fixture.yaml"))
    t0 = datetime.fromisoformat(cfg["canaries"][0]["changed_at"])
    with tempfile.TemporaryDirectory() as d:
        probes = os.path.join(d, "probes.jsonl")
        # baseline 3 days before, then twice daily for 3 weeks
        times = [t0 - timedelta(days=k) for k in (3, 2, 1)] + [t0 + timedelta(hours=12 * k + 2) for k in range(42)]
        for i, t in enumerate(times):
            run_round(cfg, probes, now=t, dry_run=True, seed=i + 1)
        # synthetic combined-format log: each crawler fetches the page some hours after the change
        log = os.path.join(d, "access.log")
        with open(log, "w") as f:
            for ua, hrs in [("OAI-SearchBot/1.0", 30), ("PerplexityBot/1.0", 9), ("Claude-SearchBot/1.0", 96), ("Googlebot/2.1", 50)]:
                ts = (t0 + timedelta(hours=hrs)).strftime("%d/%b/%Y:%H:%M:%S +0000")
                f.write(f'1.2.3.4 - - [{ts}] "GET /pricing HTTP/1.1" 200 512 "-" "Mozilla/5.0 (compatible; {ua})"\n')
        fetches = os.path.join(d, "fetches.jsonl")
        logs_main([log, "--out", fetches])
        recs = [json.loads(l) for l in open(probes)]
        fets = [json.loads(l) for l in open(fetches)]
        s = summarise(cfg, recs, fets)
        eng = s["canaries"][0]["engines"]
        assert s["simulated"] is True
        assert set(eng) == {"chatgpt", "perplexity", "claude", "gemini"}
        for name, e in eng.items():
            assert e["baseline_sees_page"] and e["baseline_sees_page"] > 0.3, name
            # first fresh answer should land near the simulated latency (within a day)
            assert e["first_fresh_h"] is not None, name
            assert abs(e["first_fresh_h"] - SIM_LATENCY_H[name]) <= 24, (name, e["first_fresh_h"])
        assert eng["perplexity"]["first_crawler_fetch_h"] == 9.0
        assert eng["chatgpt"]["first_crawler_fetch_h"] == 30.0  # OAI-SearchBot maps to ChatGPT
        assert eng["perplexity"]["first_fresh_h"] < eng["claude"]["first_fresh_h"]
        html = render_html(s)
        assert "SIMULATED DATA" in html


if __name__ == "__main__":
    test_classify_and_urls(); test_bot_identification(); test_end_to_end_dry_run()
    print("all tests passed")
