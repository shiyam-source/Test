"""Citation half-life analysis over a SlateIndex export.

    python -m halflife.analyze --data data --out out

Inputs (see DATA_REQUEST.md): responses.csv, citations.csv, mentions.csv, brands.csv (optional).
Outputs: out/summary.json, out/curves.csv.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from collections import defaultdict
from urllib.parse import urlsplit

from .spells import spells_for_series
from .survival import kaplan_meier, median_survival, survival_at, logrank

UGC = ("reddit.com", "youtube.com", "linkedin.com", "quora.com", "medium.com", "x.com", "twitter.com", "facebook.com", "stackoverflow.com")
REVIEW = ("g2.com", "capterra.com", "trustradius.com", "gartner.com", "softwareadvice.com", "getapp.com", "trustpilot.com", "peerspot.com")


def norm_url(u: str) -> str:
    p = urlsplit(u.strip() if "://" in u else "https://" + u.strip())
    return p.netloc.lower().removeprefix("www.") + (p.path.rstrip("/") or "/")


def domain(u: str) -> str:
    return norm_url(u).split("/", 1)[0]


def source_type(dom: str, vendor_domains: set[str]) -> str:
    if any(dom == d or dom.endswith("." + d) for d in vendor_domains):
        return "vendor site"
    if any(dom == d or dom.endswith("." + d) for d in UGC):
        return "community / UGC"
    if any(dom == d or dom.endswith("." + d) for d in REVIEW):
        return "review site"
    return "media / blogs / other"


def load(data):
    rows = list(csv.DictReader(open(f"{data}/responses.csv")))
    resp = {r["response_id"]: r for r in rows}
    cites, ments = defaultdict(set), defaultdict(dict)
    for r in csv.DictReader(open(f"{data}/citations.csv")):
        cites[r["response_id"]].add(norm_url(r["url"]))
    for r in csv.DictReader(open(f"{data}/mentions.csv")):
        ments[r["response_id"]][r["brand"]] = int(r.get("position") or 0)
    vend = set()
    if os.path.exists(f"{data}/brands.csv"):
        vend = {r["domain"].lower().removeprefix("www.") for r in csv.DictReader(open(f"{data}/brands.csv")) if r.get("domain")}
    return resp, cites, ments, vend


def build_spells(resp, cites, ments, vend, tol):
    runs_by_engine = defaultdict(set)
    series = defaultdict(dict)  # (engine, prompt) -> run_date -> response_id or None
    for rid, r in resp.items():
        runs_by_engine[r["engine"]].add(r["run_date"])
        series[(r["engine"], r["prompt_id"])][r["run_date"]] = rid if r["collected"] in ("1", "true", "True") else None
    out = defaultdict(list)  # kind -> list of dict(dur, event, engine, stratum)
    churn = defaultdict(lambda: [0, 0])  # kind -> [disappeared, present_before]
    for (eng, prompt), byrun in series.items():
        cal = sorted(runs_by_engine[eng])
        rids = [byrun.get(d) for d in cal]
        sets = {"url": [], "domain": [], "brand": []}
        for rid in rids:
            if rid is None:
                for k in sets: sets[k].append(None)
            else:
                urls = cites.get(rid, set())
                sets["url"].append(urls)
                sets["domain"].append({domain(u) for u in urls})
                sets["brand"].append(set(ments.get(rid, {})))
        for kind, seq in sets.items():
            items = set().union(*[s for s in seq if s])
            for it in items:
                pres = [None if s is None else (it in s) for s in seq]
                for start, dur, ev in spells_for_series(pres, tol):
                    rec = {"dur": dur, "event": ev, "engine": eng, "intent": resp[rids[start]]["intent"]}
                    if kind in ("url", "domain"):
                        rec["source"] = source_type(it if kind == "domain" else domain(it), vend)
                    else:
                        pos = ments[rids[start]].get(it, 0)
                        rec["pos"] = "top 3" if 0 < pos <= 3 else "4th or lower"
                    out[kind].append(rec)
            # week-over-week churn between consecutive collected runs
            col = [s for s in seq if s is not None]
            for a, b in zip(col, col[1:]):
                churn[kind][0] += len(a - b); churn[kind][1] += len(a)
    return out, churn


def km_summary(recs):
    d = [r["dur"] for r in recs]; e = [r["event"] for r in recs]
    curve = kaplan_meier(d, e)
    med = median_survival(curve)
    # discrete hazard h(t) = 1 - S(t)/S(t-1): chance of being dropped in week t, given alive at t-1
    hazard = [(t, round(1 - s / curve[i - 1][1], 4)) for i, (t, s, _) in enumerate(curve) if i and curve[i - 1][1] > 0]
    s4, s8 = survival_at(curve, 4), (survival_at(curve, 8) if len(curve) > 8 else None)
    return {"n_spells": len(d), "events": sum(e), "median_weeks": round(med, 2) if med else None,
            "hazard": hazard,
            "peak_hazard_week": max(hazard, key=lambda x: x[1])[0] if hazard else None,
            "cond_survive_next4_given4": round(s8 / s4, 3) if (s8 is not None and s4) else None,
            "half_life_days": round(med * 7, 1) if med else None,
            "s1": round(survival_at(curve, 1), 3), "s2": round(survival_at(curve, 2), 3),
            "s4": round(survival_at(curve, 4), 3), "s8": round(survival_at(curve, 8), 3) if len(curve) > 8 else None,
            "curve": [(t, round(s, 4)) for t, s, _ in curve]}


def analyze(data, tol=1):
    resp, cites, ments, vend = load(data)
    sp, churn = build_spells(resp, cites, ments, vend, tol)
    runs = sorted({r["run_date"] for r in resp.values()})
    res = {"simulated": os.path.exists(f"{data}/SIMULATED"), "gap_tolerance": tol,
           "runs": len(runs), "first_run": runs[0], "last_run": runs[-1],
           "responses": len(resp), "collected": sum(r["collected"] in ("1", "true", "True") for r in resp.values()),
           "engines": sorted({r["engine"] for r in resp.values()}), "categories": len({r["category"] for r in resp.values()}),
           "prompts": len({r["prompt_id"] for r in resp.values()}),
           "overall": {k: km_summary(v) for k, v in sp.items()},
           "weekly_churn": {k: round(a / b, 3) if b else None for k, (a, b) in churn.items()}}
    u, b = res["overall"]["url"], res["overall"]["brand"]
    res["brand_vs_url_ratio"] = round(b["median_weeks"] / u["median_weeks"], 1) if (u["median_weeks"] and b["median_weeks"]) else None
    chi2, p = logrank([r["dur"] for r in sp["url"]], [r["event"] for r in sp["url"]], [r["dur"] for r in sp["brand"]], [r["event"] for r in sp["brand"]])
    res["logrank_url_vs_brand"] = {"chi2": round(chi2, 1), "p": p}
    for kind in ("url", "brand"):
        res[f"{kind}_by_engine"] = {e: km_summary([r for r in sp[kind] if r["engine"] == e]) for e in res["engines"]}
        res[f"{kind}_by_intent"] = {i: km_summary([r for r in sp[kind] if r["intent"] == i]) for i in sorted({r["intent"] for r in sp[kind]})}
    res["url_by_source"] = {s: km_summary([r for r in sp["url"] if r["source"] == s]) for s in sorted({r["source"] for r in sp["url"]})}
    res["brand_by_start_position"] = {s: km_summary([r for r in sp["brand"] if r["pos"] == s]) for s in ("top 3", "4th or lower")}
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--data", default="data"); ap.add_argument("--out", default="out")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    main_res = analyze(a.data, tol=1)
    main_res["sensitivity_tol0"] = {k: v["median_weeks"] for k, v in analyze(a.data, tol=0)["overall"].items()}
    json.dump(main_res, open(f"{a.out}/summary.json", "w"), indent=1)
    with open(f"{a.out}/curves.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["kind", "week", "survival"])
        for k, v in main_res["overall"].items():
            for t, s in v["curve"]:
                w.writerow([k, t, s])
    o = main_res["overall"]
    print(("[SIMULATED] " if main_res["simulated"] else "") + f"URL half-life {o['url']['half_life_days']} d · domain {o['domain']['half_life_days']} d · brand {o['brand']['half_life_days']} d · ratio {main_res['brand_vs_url_ratio']}x")


if __name__ == "__main__":
    main()
