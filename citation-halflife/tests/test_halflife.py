import math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from halflife.spells import spells_for_series as S
from halflife.survival import kaplan_meier, median_survival, logrank


def test_spells():
    assert list(S([False, True, True, False, False, True, None, True, True], 1)) == [(1, 2, 1), (5, 3, 0)]
    assert list(S([False, True, False, True, False, False], 1)) == [(1, 3, 1)]
    assert list(S([False, True, False, True, False, False], 0)) == [(1, 1, 1), (3, 1, 1)]
    assert list(S([True, True, False, False, True], 1)) == [(4, 1, 0)]
    assert list(S([False, None, True, None, None, False, False], 1)) == [(2, 1, 1)]


def test_km_textbook():
    km = kaplan_meier([1, 2, 2, 3, 4, 4], [1, 1, 0, 1, 1, 0])
    assert abs(km[3][1] - 0.4444) < 1e-3 and abs(median_survival(km) - 2.75) < 1e-9


def test_km_recovers_constant_hazard():
    rng = random.Random(1)
    for h in (0.2, 0.5):
        d, e = [], []
        for _ in range(20000):
            t = 1
            while rng.random() > h:
                t += 1
            cens = rng.randint(1, 30)
            d.append(min(t, cens)); e.append(int(t <= cens))
        km = kaplan_meier(d, e)
        # discrete survival: S(t) = (1-h)^t  -> check S(2) under censoring
        assert abs(km[2][1] - (1 - h) ** 2) < 0.02, (h, km[2][1])


def test_logrank_detects_difference():
    rng = random.Random(2)
    g = lambda h: [next(t for t in range(1, 99) if rng.random() < h) for _ in range(800)]
    a, b = g(0.5), g(0.15)
    chi2, p = logrank(a, [1] * len(a), b, [1] * len(b))
    assert p < 1e-6
    chi2, p = logrank(a, [1] * len(a), g(0.5), [1] * 800)
    assert p > 0.001


if __name__ == "__main__":
    test_spells(); test_km_textbook(); test_km_recovers_constant_hazard(); test_logrank_detects_difference(); print("all tests passed")
