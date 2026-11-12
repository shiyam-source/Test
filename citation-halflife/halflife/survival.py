"""Kaplan-Meier estimation and log-rank test for weekly (discrete) spell data.

A *spell* is an uninterrupted run of weeks in which an item (a cited URL, or a
named brand) appears in the answer to the same prompt on the same engine.
duration = number of consecutive runs present; event = 1 if the spell ended
(observed absent), 0 if still alive at the last run (right-censored).
"""
from __future__ import annotations

import math
from collections import Counter


def kaplan_meier(durations: list[int], events: list[int]) -> list[tuple[int, float, int]]:
    """Return [(t, S(t), at_risk)] for t = 0..max duration. S(0) = 1."""
    n = len(durations)
    deaths = Counter(d for d, e in zip(durations, events) if e)
    leaving = Counter(durations)
    at_risk, s, out = n, 1.0, [(0, 1.0, n)]
    for t in range(1, max(durations, default=0) + 1):
        d = deaths.get(t, 0)
        if at_risk > 0 and d:
            s *= 1 - d / at_risk
        out.append((t, s, at_risk))
        at_risk -= leaving.get(t, 0)
    return out


def median_survival(curve: list[tuple[int, float, int]]) -> float | None:
    """First time S(t) <= 0.5, linearly interpolated between steps. None if never reached."""
    prev_t, prev_s = 0, 1.0
    for t, s, _ in curve:
        if s <= 0.5:
            if s == prev_s:
                return float(t)
            return prev_t + (prev_s - 0.5) / (prev_s - s) * (t - prev_t)
        prev_t, prev_s = t, s
    return None


def survival_at(curve, t: int) -> float:
    for tt, s, _ in curve:
        if tt == t:
            return s
    return curve[-1][1] if curve else float("nan")


def logrank(d1: list[int], e1: list[int], d2: list[int], e2: list[int]) -> tuple[float, float]:
    """Two-group log-rank test. Returns (chi2, p) with 1 degree of freedom."""
    times = sorted({d for d, e in zip(d1 + d2, e1 + e2) if e})
    obs_minus_exp, var = 0.0, 0.0
    for t in times:
        n1 = sum(1 for d in d1 if d >= t); n2 = sum(1 for d in d2 if d >= t)
        o1 = sum(1 for d, e in zip(d1, e1) if d == t and e); o2 = sum(1 for d, e in zip(d2, e2) if d == t and e)
        n, o = n1 + n2, o1 + o2
        if n < 2:
            continue
        exp1 = o * n1 / n
        obs_minus_exp += o1 - exp1
        var += o * (n1 / n) * (1 - n1 / n) * (n - o) / (n - 1)
    if var == 0:
        return 0.0, 1.0
    chi2 = obs_minus_exp ** 2 / var
    p = math.erfc(math.sqrt(chi2 / 2))  # survival function of chi-square with 1 df
    return chi2, p
