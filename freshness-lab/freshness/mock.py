"""Simulated engines for dry runs. Output is clearly labelled SIMULATED and must
never be reported as a finding. Each engine flips from the old value to the new
one after a fixed simulated latency, with some run-to-run noise."""
from __future__ import annotations

import random
from datetime import datetime

from .engines import ProbeResult

# hours after the change at which each simulated engine starts returning the new value
SIM_LATENCY_H = {"perplexity": 20, "chatgpt": 44, "gemini": 70, "claude": 120}


def make_mock(engine: str, canary: dict, now: datetime, rng: random.Random):
    def _probe(prompt: str, model: str) -> ProbeResult:
        changed = datetime.fromisoformat(canary["changed_at"])
        hours = (now - changed).total_seconds() / 3600
        lat = SIM_LATENCY_H[engine]
        p_new = 0.0 if hours < 0 else min(1.0, max(0.0, (hours - lat) / 24 + 0.5)) if hours >= lat - 12 else 0.0
        if rng.random() < 0.08:
            text = "I could not find current pricing information."
            cited = []
        elif rng.random() < p_new:
            text = f"According to the official page, it is {canary['new_value']}."
            cited = [canary["url"]]
        else:
            text = f"It costs {canary['old_value']}."
            cited = [canary["url"]] if rng.random() < 0.6 else ["https://example-listicle.com/best-tools"]
        return ProbeResult(engine=engine, model=f"SIMULATED-{model}", text=text, cited_urls=cited, latency_s=0.0)
    return _probe
