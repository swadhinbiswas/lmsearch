"""Rule-based query parser: RAM, storage, CPU, brand, price (USD), category.

Deterministic and fast. The LLM layer (next phase) calls this as validator/repair.
"""

from __future__ import annotations

import re

BRANDS = [
    "lenovo",
    "hp",
    "dell",
    "asus",
    "acer",
    "msi",
    "apple",
    "samsung",
    "xiaomi",
    "realme",
    "oneplus",
    "vivo",
    "oppo",
    "google",
    "motorola",
    "huawei",
    "infinix",
]
LAPTOP_HINTS = [
    "laptop",
    "notebook",
    "macbook",
    "thinkpad",
    "ultrabook",
    "ryzen",
    "intel",
    "core i",
    "ssd",
]
PHONE_HINTS = ["phone", "mobile", "smartphone", "android", "iphone", "5g", "mah", "camera"]
USE_CASES = [
    "gaming",
    "programming",
    "coding",
    "office",
    "student",
    "study",
    "video editing",
    "design",
]

RAM_RE = re.compile(r"(\d{1,3})\s*gb\s*(?:ram)?", re.I)
STORAGE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(tb|gb)\b", re.I)
PRICE_UNDER = re.compile(
    r"(?:under|below|less than|<|<=|within|upto|up to)\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(k\b)?", re.I
)
PRICE_OVER = re.compile(r"(?:over|above|more than|>|>=)\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(k\b)?", re.I)
PRICE_BETWEEN = re.compile(
    r"between\s*\$?\s*([\d,]+)\s*(k\b)?\s*and\s*\$?\s*([\d,]+)\s*(k\b)?", re.I
)
DOLLAR_FIND = re.compile(r"\$\s*([\d,]+(?:\.\d+)?)\s*(k\b)?", re.I)
REFRESH_RE = re.compile(r"(\d{2,3})\s*hz", re.I)
BATTERY_RE = re.compile(r"(\d{3,5})\s*mah", re.I)
SCREEN_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:inch|in\b|\"|display)", re.I)


def _num(s: str) -> float:
    return float(s.replace(",", ""))


def _expand_k(v: float, k: str | None) -> float:
    return v * 1000 if k else v


def detect_category(q: str) -> str | None:
    low = q.lower()
    ls = sum(1 for h in LAPTOP_HINTS if h in low)
    ps = sum(1 for h in PHONE_HINTS if h in low)
    if ls > ps and ls > 0:
        return "laptop"
    if ps > ls and ps > 0:
        return "phone"
    return None


def detect_brands(q: str) -> list[str]:
    low = q.lower()
    found = []
    for b in BRANDS:
        if re.search(rf"\b{re.escape(b)}\b", low):
            found.append(b.capitalize() if b != "hp" else "HP")
    return found


def detect_cpu_series(q: str) -> list[str]:
    low = q.lower()
    out = []
    if "ryzen" in low:
        m = re.search(r"ryzen\s*([3579])", low)
        out.append(f"ryzen{m.group(1)}" if m else "ryzen")
    for i in ["i3", "i5", "i7", "i9"]:
        if re.search(rf"\b{i}\b", low) or re.search(rf"core\s*{i}", low):
            out.append(i)
    for mchip in ["m1", "m2", "m3"]:
        if re.search(rf"\b{mchip}\b", low):
            out.append(mchip)
    return out


def parse_price_usd(q: str) -> dict:
    low = q.lower()
    m = PRICE_BETWEEN.search(q)
    if m:
        lo = _expand_k(_num(m.group(1)), m.group(2))
        hi = _expand_k(_num(m.group(3)), m.group(4))
        return {"min": lo, "max": hi, "currency": "USD"}
    m = PRICE_UNDER.search(q)
    if m:
        return {"min": None, "max": _expand_k(_num(m.group(1)), m.group(2)), "currency": "USD"}
    m = PRICE_OVER.search(q)
    if m:
        return {"min": _expand_k(_num(m.group(1)), m.group(2)), "max": None, "currency": "USD"}
    m = DOLLAR_FIND.search(q)
    if m:
        v = _expand_k(_num(m.group(1)), m.group(2))
        if re.search(r"under|below|less|<", low):
            return {"min": None, "max": v, "currency": "USD"}
        return {"min": None, "max": v, "currency": "USD"}
    return {}


def parse_query_rule(q: str) -> dict:
    must: dict = {}
    m = RAM_RE.search(q)
    if m:
        v = int(m.group(1))
        if 2 <= v <= 256:
            must["ram_gb_min"] = v
    m = STORAGE_RE.search(q)
    if m:
        val, unit = float(m.group(1)), m.group(2).lower()
        gb = int(val * 1024) if unit == "tb" else int(val)
        if 8 <= gb <= 8192:
            must["storage_gb_min"] = gb
    cpu = detect_cpu_series(q)
    if cpu:
        must["cpu_series"] = cpu
    m = REFRESH_RE.search(q)
    if m:
        must["refresh_hz_min"] = int(m.group(1))
    m = BATTERY_RE.search(q)
    if m:
        must["battery_mah_min"] = int(m.group(1))
    low = q.lower()
    use = [u for u in USE_CASES if u in low]
    soft = []
    if "lightweight" in low or "light weight" in low:
        soft.append("lightweight")
    if "long battery" in low:
        soft.append("long-battery")
    return {
        "category": detect_category(q),
        "brands": detect_brands(q),
        "must": must,
        "price": parse_price_usd(q),
        "use_case": use,
        "soft_preferences": soft,
        "exclude": [],
        "semantic_query": q.strip(),
    }
