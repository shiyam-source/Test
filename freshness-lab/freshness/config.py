from __future__ import annotations

import yaml


def load(path: str) -> dict:
    with open(path) as f:
        cfg = yaml.safe_load(f)
    for c in cfg.get("canaries", []):
        c.setdefault("arm", "no-ping")
        c.setdefault("new_patterns", [__import__("re").escape(str(c["new_value"]))])
        c.setdefault("old_patterns", [__import__("re").escape(str(c["old_value"]))])
        c["changed_at"] = str(c["changed_at"])
    return cfg
