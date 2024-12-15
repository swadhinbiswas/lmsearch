"""Small text helpers."""

import re

_WS = re.compile(r"\s+")


def normalize_ws(s: str) -> str:
    return _WS.sub(" ", (s or "").strip().lower())
