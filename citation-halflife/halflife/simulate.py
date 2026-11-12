"""Synthetic SlateIndex-shaped export for building and testing the pipeline.
Writes data/SIMULATED so every downstream output is watermarked. Never publish."""
from __future__ import annotations

import csv
import os
import random
from datetime import date, timedelta

ENGINES = {"chatgpt": (5, 0.48), "perplexity": (9, 0.58), "ai_mode": (7, 0.52)}  # urls per answer, weekly URL stay prob
SOURCE_STAY = {"vendor": 0.12, "review": 0.08, "ugc": -0.12, "media": 0.0}
UGC = ["reddit.com", "youtube.com", "linkedin.com", "quora.com", "medium.com"]
REVIEW = ["g2.com", "capterra.com", "trustradius.com", "gartner.com", "softwareadvice.com"]


def main(out="data", n_cat=33, n_prompt=30, n_runs=14, seed=7):
    rng = random.Random(seed)
    os.makedirs(out, exist_ok=True)
    runs = [date(2026, 8, 10) + timedelta(weeks=k) for k in range(n_runs)]
    R = open(f"{out}/responses.csv", "w", newline=""); C = open(f"{out}/citations.csv", "w", newline="")
    M = open(f"{out}/mentions.csv", "w", newline=""); B = open(f"{out}/brands.csv", "w", newline="")
    rw, cw, mw, bw = csv.writer(R), csv.writer(C), csv.writer(M), csv.writer(B)
    rw.writerow(["response_id", "run_date", "engine", "category", "prompt_id", "intent", "collected"])
    cw.writerow(["response_id", "url"]); mw.writerow(["response_id", "brand", "position"]); bw.writerow(["brand", "domain"])
    rid = 0
    for c in range(n_cat):
        brands = [f"brand{c}_{b}" for b in range(14)]
        for b in brands:
            bw.writerow([b, f"{b}.com"])
        for p in range(n_prompt):
            intent = ["informational", "commercial", "transactional", "navigational"][p % 4]
            for eng, (k_urls, stay) in ENGINES.items():
                cur_b = set(rng.sample(brands, 5)); cur_u = {}
                for r, d in enumerate(runs):
                    rid += 1
                    collected = rng.random() > 0.03
                    rw.writerow([rid, d.isoformat(), eng, f"cat{c}", f"c{c}p{p}", intent, int(collected)])
                    # brands: high persistence
                    cur_b = {b for b in cur_b if rng.random() < 0.88}
                    while len(cur_b) < 5:
                        cur_b.add(rng.choice(brands))
                    # urls: lower persistence, source-type dependent
                    cur_u = {u: t for u, t in cur_u.items() if rng.random() < stay + SOURCE_STAY[t]}
                    while len(cur_u) < k_urls:
                        t = rng.choices(["vendor", "review", "ugc", "media"], [0.35, 0.15, 0.2, 0.3])[0]
                        if t == "vendor":
                            host = rng.choice(brands) + ".com"
                        elif t == "review":
                            host = rng.choice(REVIEW)
                        elif t == "ugc":
                            host = rng.choice(UGC)
                        else:
                            host = f"blog{rng.randint(1, 400)}.com"
                        cur_u[f"https://{host}/page-{rng.randint(1, 60)}"] = t
                    if not collected:
                        continue
                    for pos, b in enumerate(sorted(cur_b, key=lambda _: rng.random()), 1):
                        mw.writerow([rid, b, pos])
                    for u in cur_u:
                        cw.writerow([rid, u])
    for f in (R, C, M, B):
        f.close()
    open(f"{out}/SIMULATED", "w").write("synthetic data - do not publish\n")
    print(f"simulated {rid} responses over {n_runs} runs -> {out}/")


if __name__ == "__main__":
    main()
