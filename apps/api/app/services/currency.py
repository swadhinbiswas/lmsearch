"""Currency + South-Asian unit handling: k/lakh/BDT/USD/৳, under/below/around/between."""
from __future__ import annotations

import re

BDT_PER_USD = 117.0

BDT_HINT = re.compile(r"(bdt|taka|৳|taka\b|tk\b)", re.I)
LAKH_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(lakh|lac|laks?)\b", re.I)
K_RE = re.compile(r"(\d+(?:\.\d+)?)\s*k\b", re.I)
NUM_RE = re.compile(r"[\d,]+(?:\.\d+)?")
BETWEEN_RE = re.compile(r"between\s+(.+?)\s+and\s+(.+)", re.I)
AROUND_RE = re.compile(r"(?:around|about|~|almost|near)\s*(.+)", re.I)
UNDER_RE = re.compile(r"(?:under|below|less than|within|up ?to|<=?)\s*(.+)", re.I)
OVER_RE = re.compile(r"(?:over|above|more than|>=?)\s*(.+)", re.I)


def detect_currency(text: str) -> str:
    if BDT_HINT.search(text or ""):
        return "BDT"
    if "$" in (text or "") or "usd" in (text or "").lower():
        return "USD"
    return "USD"


def _reject_absurd(v: float | None) -> float | None:
    if v is not None and v > 100_000_000:
        return None
    return v


def parse_amount(chunk: str) -> float | None:
    if not chunk:
        return None
    c = chunk.replace(",", "").lower()
    m = LAKH_RE.search(c)
    if m:
        return float(m.group(1)) * 100000
    m = K_RE.search(c)
    if m:
        return float(m.group(1)) * 1000
    m = NUM_RE.search(c)
    if m:
        try:
            return _reject_absurd(float(m.group(0)))
        except ValueError:
            return None
    return None


def to_usd(amount: float, currency: str) -> float:
    if currency == "BDT":
        return round(amount / BDT_PER_USD, 2)
    return amount


def parse_price(text: str) -> dict:
    """Return {min,max,currency,original} in ORIGINAL currency + usd bounds."""
    if not text:
        return {}
    cur = detect_currency(text)
    low = text.lower()
    m = BETWEEN_RE.search(text)
    if m:
        lo, hi = parse_amount(m.group(1)), parse_amount(m.group(2))
        if lo is not None and hi is not None:
            return {"min": lo, "max": hi, "currency": cur,
                    "min_usd": to_usd(lo, cur), "max_usd": to_usd(hi, cur)}
    m = AROUND_RE.search(text)
    if m:
        v = parse_amount(m.group(1))
        if v is not None:
            return {"min": round(v * 0.85, 2), "max": round(v * 1.15, 2), "currency": cur,
                    "min_usd": to_usd(v * 0.85, cur), "max_usd": to_usd(v * 1.15, cur)}
    m = UNDER_RE.search(text)
    if m:
        v = parse_amount(m.group(1))
        if v is not None:
            return {"min": None, "max": v, "currency": cur, "max_usd": to_usd(v, cur)}
    m = OVER_RE.search(text)
    if m:
        v = parse_amount(m.group(1))
        if v is not None:
            return {"min": v, "max": None, "currency": cur, "min_usd": to_usd(v, cur)}
    # bare amounts: "40k BDT", "৳50000", "$1200"
    if BDT_HINT.search(text) or "$" in text or "usd" in low or NUM_RE.search(text):
        v = parse_amount(text)
        # only treat as price when currency marker or price verb present
        if v is not None and (BDT_HINT.search(text) or "$" in text or "usd" in low
                              or re.search(r"under|below|price|budget|dham|dam", low)):
            if re.search(r"under|below|less|up ?to", low):
                return {"min": None, "max": v, "currency": cur, "max_usd": to_usd(v, cur)}
            return {"min": None, "max": v, "currency": cur, "max_usd": to_usd(v, cur)}
    return {}


BANGLA_MAP = {
    "ল্যাপটপ": "laptop",
    "ফোন": "phone",
    "মোবাইল": "phone",
    "দাম": "price",
    "বাজেট": "budget",
    "গেমিং": "gaming",
    "কম": "under",
    "নিচে": "under",
    "উপরে": "above",
    "হাজার": "thousand",
    "লাখ": "lakh",
    "টাকা": "BDT",
    "৳": "BDT",
}


def transliterate_mixed(text: str) -> str:
    out = text or ""
    for bn, en in BANGLA_MAP.items():
        out = out.replace(bn, f" {en} ")
    # common romanized typos / variants
    fixes = {
        "labtop": "laptop", "laptap": "laptop", "leptop": "laptop",
        "ryzenn": "ryzen", "ryzen ": "ryzen ", "32 gb": "32gb", "16 gb": "16gb", "8 gb": "8gb",
        "sumsung": "samsung", "xiaomi ": "xiaomi ", " battary ": " battery ",
    }
    low = out.lower()
    for k, v in fixes.items():
        low = low.replace(k, v)
    return low
