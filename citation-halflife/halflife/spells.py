"""Turn weekly presence data into spells.

Rules (all configurable, all reported in the write-up):
- A response that was scheduled but not collected is MISSING, not absent. A
  missing week neither extends nor ends a spell; it is skipped.
- gap_tolerance = 1 means an item must be absent for 2 consecutive collected
  runs before its spell counts as ended (one-week flickers are not deaths).
  Report results at tolerance 0 and 1 as a sensitivity check.
- Left truncation: spells already alive at the first collected run have an
  unknown start, so only spells that START after it are kept ("incident
  spells"). Spells still alive at the last run are right-censored.
"""
from __future__ import annotations


def spells_for_series(present: list[bool | None], gap_tolerance: int = 1):
    """present[i] = True / False / None (missing) for consecutive weekly runs.

    Yields (start_run_index, duration_in_collected_runs, event) where duration
    runs from the first to the last present run of the spell (tolerated gaps
    inside count), and event = 1 if the spell was observed to end.
    """
    collected = [(i, v) for i, v in enumerate(present) if v is not None]
    vals = [v for _, v in collected]
    n, i = len(vals), 0
    while i < n:
        if not vals[i]:
            i += 1
            continue
        start = last_present = i
        gap, ended, j = 0, False, i + 1
        while j < n:
            if vals[j]:
                last_present, gap = j, 0
            else:
                gap += 1
                if gap > gap_tolerance:
                    ended = True
                    break
            j += 1
        if start > 0:
            yield collected[start][0], last_present - start + 1, int(ended)
        i = j if ended else n
