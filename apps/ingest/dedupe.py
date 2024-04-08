"""Fuzzy title dedupe. rapidfuzz when available, difflib fallback (no heavy dep in tests)."""

from __future__ import annotations

try:
    from rapidfuzz import fuzz as _fuzz

    def similarity(a: str, b: str) -> float:
        return _fuzz.token_set_ratio(a.lower(), b.lower()) / 100.0

except Exception:  # pragma: no cover - fallback path
    import difflib

    def similarity(a: str, b: str) -> float:
        return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def is_duplicate(title_a: str, title_b: str, threshold: float = 0.88) -> bool:
    return similarity(title_a, title_b) >= threshold


def dedupe_items(items: list[dict], threshold: float = 0.88) -> list[dict]:
    kept: list[dict] = []
    for item in items:
        title = item.get("title", "")
        if any(is_duplicate(title, k.get("title", ""), threshold) for k in kept):
            continue
        kept.append(item)
    return kept
