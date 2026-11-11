"""Classify an answer against a canary: did the engine see the new value?"""
from __future__ import annotations

import re
from urllib.parse import urlsplit

STATUSES = ("new", "both", "old", "neither", "error")


def normalise_url(u: str) -> str:
    u = u.split("#", 1)[0].strip()
    p = urlsplit(u if "://" in u else "https://" + u)
    host = p.netloc.lower().removeprefix("www.")
    path = p.path.rstrip("/") or "/"
    return f"{host}{path}"


def classify(text: str, new_patterns: list[str], old_patterns: list[str], error: str | None = None) -> str:
    if error:
        return "error"
    has_new = any(re.search(p, text, re.I) for p in new_patterns)
    has_old = any(re.search(p, text, re.I) for p in old_patterns)
    if has_new and has_old:
        return "both"  # e.g. "was $499, now $449" - the engine knows about the change
    if has_new:
        return "new"
    if has_old:
        return "old"
    return "neither"


def cites_canary(cited_urls: list[str], canary_url: str) -> bool:
    target = normalise_url(canary_url)
    return any(normalise_url(u) == target for u in cited_urls)


def is_fresh(status: str) -> bool:
    return status in ("new", "both")
