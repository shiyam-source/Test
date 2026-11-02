"""Statistical analysis behind the Coin-Flip Report and the Quota Tax study.
Everything here is computed from first principles (binomial sampling) plus
publicly reported plan figures. No AI answers were collected."""
import json, math, csv, os
import numpy as np
from scipy.stats import norm

OUT = os.path.join(os.path.dirname(__file__), "..", "data")
rng = np.random.default_rng(20261102)
Z = 1.959964
ZB = norm.ppf(0.80)

def wilson(p, n):
    if n == 0: return (0, 1)
    d = 1 + Z**2 / n
    c = (p + Z**2 / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z**2 / (4 * n * n)) / d
    return (max(0, c - h), min(1, c + h))

def n_needed(p1, p2):
    pb = (p1 + p2) / 2
    num = (Z * math.sqrt(2 * pb * (1 - pb)) + ZB * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return num / (p2 - p1) ** 2

def mdc(p, n):
    """Smallest upward change from baseline p detectable at 80% power, alpha .05, n per period."""
    lo, hi = 1e-4, 1 - p - 1e-4
    for _ in range(80):
        mid = (lo + hi) / 2
        if n_needed(p, p + mid) > n: lo = mid
        else: hi = mid
    return hi

res = {}

# 1. Interval width by samples per prompt-engine
ns = [7, 25, 30, 60, 90, 100, 250, 500, 1000]
rows = []
for n in ns:
    for p in (0.10, 0.30, 0.50):
        lo, hi = wilson(p, n)
        rows.append(dict(n=n, p=p, lo=round(lo, 4), hi=round(hi, 4), width=round(hi - lo, 4), mdc=round(mdc(p, n), 4)))
res["intervals"] = rows

# 2. Answers needed per period to detect a change from 30%
res["n_for_change"] = {f"{d}pt": math.ceil(n_needed(0.30, 0.30 + d / 100)) for d in (5, 10, 15, 20, 25)}
# answers needed for a +/- X point 95% interval at p=.3 (normal approx)
res["n_for_halfwidth"] = {f"{h}pt": math.ceil(Z**2 * 0.21 / (h / 100) ** 2) for h in (5, 10, 15)}

# 3. Plan designs -> samples per prompt-engine per month
plans = [
    ("Profound 7-day trial", 50, 3, 7, "Reported trial: 50 prompts, 3 engines, daily for 7 days"),
    ("Profound Starter (removed Sep 2026)", 50, 1, 30, "50 prompts, ChatGPT only, daily"),
    ("Profound Growth / agency workspace", 100, 3, 30, "100 prompts, 3 engines, daily"),
    ("Slate Growth, breadth allocation", 333, 1, 30, "10,000-answer pool spread across 333 prompts"),
    ("Slate Growth, even allocation", 100, 4, 25, "10,000-answer pool: 100 prompts x 4 engines x 25 runs"),
    ("Slate Growth, focus allocation", 40, 4, 60, "~9,600 answers: 40 priority prompts x 4 engines x 60 runs"),
]
pr = []
for name, prompts, eng, runs, note in plans:
    lo, hi = wilson(0.30, runs)
    pr.append(dict(plan=name, prompts=prompts, engines=eng, runs=runs, answers=prompts * eng * runs,
                   lo=round(lo, 3), hi=round(hi, 3), mdc=round(mdc(0.30, runs), 3),
                   mdc_pooled_engines=round(mdc(0.30, runs * eng), 3), note=note))
res["plans"] = pr

# 4. Phantom-move simulation: true rates never change.
def phantom(prompts=100, engines=3, runs=30, months=12, threshold=0.10, sims=200):
    flags, prompt_months, brand_swings = 0, 0, []
    for _ in range(sims):
        true = rng.beta(3, 7, size=(prompts, engines))  # mean 0.30, real prompts differ
        obs = rng.binomial(runs, true[None, :, :].repeat(months, 0)) / runs  # months x prompts x engines
        diffs = np.abs(np.diff(obs, axis=0))
        flags += (diffs >= threshold).sum(); prompt_months += diffs.size
        brand = obs.mean(axis=(1, 2)); brand_swings.append(np.abs(np.diff(brand)).max())
    return flags / prompt_months, float(np.mean(brand_swings))

sim = []
for label, runs in (("7 runs (trial-style)", 7), ("30 runs (daily)", 30), ("60 runs", 60), ("100 runs", 100), ("250 runs", 250)):
    f10, bs = phantom(runs=runs)
    f20, _ = phantom(runs=runs, threshold=0.20, sims=60)
    sim.append(dict(design=label, runs=runs, phantom_10pt=round(float(f10), 3), phantom_20pt=round(float(f20), 3), brand_max_swing=round(bs, 4)))
res["phantom"] = sim

# 5. Phantom leaderboard: 5 brands, fixed true rates, how often is the true leader ranked #1?
true = np.array([0.34, 0.31, 0.30, 0.28, 0.25])
lb = []
for runs in (7, 30, 60, 100, 250, 1000):
    obs = rng.binomial(runs, true, size=(20000, 5)) / runs
    noise = rng.random((20000, 5)) * 1e-9  # random tie-break
    top = np.argmax(obs + noise, axis=1)
    order_ok = np.all(np.diff(obs + noise, axis=1) < 0, axis=1)
    lb.append(dict(runs=runs, leader_correct=round(float((top == 0).mean()), 3),
                   order_correct=round(float(order_ok.mean()), 4),
                   true_leader_ranked_3rd_or_worse=round(float((np.argsort(-(obs + noise), axis=1)[:, :2] != 0).all(axis=1).mean()), 3)))
res["leaderboard"] = lb

# 6. Cluster pooling with heterogeneous prompts (design effect)
def cluster_mdc_sim(k_prompts, runs, engines=3, sims=3000, lift=0.0):
    out = []
    for _ in range(sims):
        t = rng.beta(3, 7, size=(k_prompts, engines))
        a = rng.binomial(runs, t).sum() / (k_prompts * engines * runs)
        b = rng.binomial(runs, np.clip(t + lift, 0, 1)).sum() / (k_prompts * engines * runs)
        out.append(b - a)
    return float(np.std(out))
cl = []
for k in (1, 5, 10, 25):
    sd = cluster_mdc_sim(k, 30)
    cl.append(dict(prompts_in_cluster=k, answers_per_month=k * 3 * 30, sd_of_change=round(sd, 4), approx_mdc=round(2.8 * sd, 4)))
res["clusters"] = cl

# ---------- Quota Tax ----------
vendors = [  # name, monthly price, prompts, answers/mo, note, status
    ("Otterly Lite", 29, 15, 15 * 30 * 1, "15 prompts; answers assume 1 engine daily"),
    ("Otterly Standard", 189, 100, None, "100 prompts"),
    ("Peec Starter", 95, 50, 50 * 3 * 30, "50 prompts, 3 models, daily"),
    ("Peec Pro", 245, 150, 150 * 3 * 30, "150 prompts, 3 models, daily"),
    ("Scrunch Starter", 300, 350, None, "350 prompts (sources conflict)"),
    ("AthenaHQ Starter", 295, None, 3600, "3,600 credits = 3,600 responses"),
    ("Ahrefs custom prompts", 50, None, 2500, "add-on: 2,500 checks; base plan may be required"),
    ("Profound Starter (removed)", 99, 50, 1500, "50 prompts, ChatGPT, daily; removed Sep 2026"),
    ("Profound Growth (removed)", 399, 100, 9000, "100 prompts, 3 engines, daily; removed Sep 2026"),
    ("Profound agency workspace", 399, 100, 9000, "per client, +$99/mo agency base"),
    ("Slate Growth", 499, None, 10000, "unlimited prompts; 10,000 answers; +15,000 execution credits"),
]
vt = []
for n, price, prompts, answers, note in vendors:
    vt.append(dict(vendor=n, price=price, prompts=prompts, answers=answers,
                   per_prompt=round(price / prompts, 2) if prompts else None,
                   per_answer=round(price / answers, 4) if answers else None, note=note))
res["vendors"] = vt

# cost & time to a decision-grade reading (±10 pts at p=.3, n=81) per prompt-engine
need10 = res["n_for_halfwidth"]["10pt"]; need5 = res["n_for_halfwidth"]["5pt"]
dg = []
for n, per_ans, cadence in (("Profound agency workspace", 399 / 9000, 30), ("Slate Growth (gross)", 499 / 10000, None),
                            ("Slate Growth (net of credits)", (499 - 375) / 10000, None), ("AthenaHQ Starter", 295 / 3600, None),
                            ("Peec Starter", 95 / 4500, 30), ("Ahrefs custom prompts", 50 / 2500, None)):
    dg.append(dict(vendor=n, per_answer=round(per_ans, 4), cost_10pt=round(per_ans * need10, 2), cost_5pt=round(per_ans * need5, 2),
                   months_to_10pt_fixed_daily=round(need10 / cadence, 1) if cadence else None,
                   months_to_5pt_fixed_daily=round(need5 / cadence, 1) if cadence else None))
res["decision_grade"] = dg

# agency portfolio
ag = []
for c in range(1, 31):
    ag.append(dict(clients=c, profound=99 + 399 * c, peec_starter=95 * c, otterly_standard=189 * c, slate_agency_reported=2000))
res["agency"] = ag
res["agency_crossover_clients"] = (2000 - 99) / 399

json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1)
for key in ("intervals", "plans", "phantom", "leaderboard", "clusters", "vendors", "decision_grade"):
    with open(os.path.join(OUT, f"{key}.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(res[key][0].keys())); w.writeheader(); w.writerows(res[key])
print(json.dumps({k: v for k, v in res.items() if k != "agency"}, indent=1))
