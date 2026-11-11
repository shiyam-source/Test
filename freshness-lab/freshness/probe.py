"""Run one probe round: every active canary x prompt x engine x repetition.

Appends one JSON line per answer to data/probes.jsonl. Run it on a schedule
(daily, or twice daily during the first week after a change).

    python -m freshness.probe --config config/canaries.yaml            # live
    python -m freshness.probe --config config/canaries.yaml --dry-run  # simulated
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone

from . import config as cfgmod
from .detect import classify, cites_canary
from .engines import ADAPTERS
from .mock import make_mock


def run_round(cfg: dict, out_path: str, now: datetime | None = None, dry_run: bool = False, seed: int = 0) -> int:
    now = now or datetime.now(timezone.utc)
    rng = random.Random(seed or int(now.timestamp()))
    reps = int(cfg.get("repetitions", 2))
    engines = cfg.get("engines", {})
    n = 0
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "a") as out:
        for canary in cfg["canaries"]:
            if canary.get("active", True) is False:
                continue
            for pi, prompt in enumerate(canary["prompts"]):
                for eng, ecfg in engines.items():
                    if not ecfg.get("enabled", True):
                        continue
                    fn = make_mock(eng, canary, now, rng) if dry_run else ADAPTERS[eng]
                    for rep in range(reps):
                        res = fn(prompt, ecfg["model"])
                        rec = {
                            "ts": now.isoformat(),
                            "canary": canary["id"],
                            "arm": canary["arm"],
                            "page_type": canary.get("page_type"),
                            "prompt_idx": pi,
                            "rep": rep,
                            "simulated": dry_run,
                            "status": classify(res.text, canary["new_patterns"], canary["old_patterns"], res.error),
                            "cites_canary_url": cites_canary(res.cited_urls, canary["url"]),
                            **res.to_dict(),
                        }
                        out.write(json.dumps(rec) + "\n")
                        n += 1
    return n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/canaries.yaml")
    ap.add_argument("--out", default="data/probes.jsonl")
    ap.add_argument("--dry-run", action="store_true", help="use simulated engines; output is labelled simulated")
    a = ap.parse_args(argv)
    cfg = cfgmod.load(a.config)
    n = run_round(cfg, a.out, dry_run=a.dry_run)
    print(f"wrote {n} probe records to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
