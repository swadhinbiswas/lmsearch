"""Hard spec filters (SQL-equivalent on dicts) + progressive relaxation.

Relaxation order (cheapest to drop first): brand → price(+20%) → battery/refresh →
storage → ram → cpu. Reports what was relaxed.
"""
from __future__ import annotations


def spec_val(p: dict, key: str, default=None):
    return p.get("specs", {}).get(key, default)


def matches(p: dict, parsed: dict) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    must = parsed.get("must", {}) or {}
    # category
    if parsed.get("category") and p.get("category") != parsed["category"]:
        return False, ["category"]
    # brands
    brands = [b.lower() for b in (parsed.get("brands") or [])]
    if brands and p.get("brand", "").lower() not in brands:
        return False, ["brand"]
    # ram
    if must.get("ram_gb_min") is not None:
        if (spec_val(p, "ram_gb", 0) or 0) < must["ram_gb_min"]:
            return False, ["ram_gb_min"]
    if must.get("storage_gb_min") is not None:
        if (spec_val(p, "storage_gb", 0) or 0) < must["storage_gb_min"]:
            return False, ["storage_gb_min"]
    if must.get("cpu_series"):
        want = [c.lower() for c in must["cpu_series"]]
        have = f"{spec_val(p,'cpu_brand','')} {spec_val(p,'cpu_model','')} {spec_val(p,'cpu_series','')} {spec_val(p,'chipset','')}".lower()
        if not any(w in have for w in want):
            return False, ["cpu_series"]
    if must.get("refresh_hz_min") is not None:
        if (spec_val(p, "refresh_hz", 0) or 0) < must["refresh_hz_min"]:
            return False, ["refresh_hz_min"]
    if must.get("battery_mah_min") is not None:
        if (spec_val(p, "battery_mah", 0) or 0) < must["battery_mah_min"]:
            return False, ["battery_mah_min"]
    # price (USD catalog)
    price = parsed.get("price") or {}
    if price.get("max") is not None and float(p.get("price", 0)) > float(price["max"]):
        return False, ["price_max"]
    if price.get("min") is not None and float(p.get("price", 0)) < float(price["min"]):
        return False, ["price_min"]
    return True, reasons


RELAX_ORDER = ["brand", "price_max", "price_min", "refresh_hz_min", "battery_mah_min", "storage_gb_min", "ram_gb_min", "cpu_series"]


def apply_filters(catalog: list[dict], parsed: dict) -> tuple[list[dict], list[str]]:
    ok = [p for p in catalog if matches(p, parsed)[0]]
    if len(ok) >= 5 or not any([parsed.get("must"), parsed.get("price"), parsed.get("brands")]):
        return ok, []
    relaxed: list[str] = []
    work = {k: (dict(v) if isinstance(v, dict) else (list(v) if isinstance(v, list) else v)) for k, v in parsed.items()}
    work["must"] = dict(parsed.get("must", {}) or {})
    work["price"] = dict(parsed.get("price", {}) or {})
    for step in RELAX_ORDER:
        if len(ok) >= 5:
            break
        if step == "brand" and work.get("brands"):
            work["brands"] = []
            relaxed.append("brand")
        elif step in ("price_max", "price_min") and work.get("price"):
            if step == "price_max" and work["price"].get("max") is not None:
                orig = float(parsed.get("price", {}).get("max") or work["price"]["max"])
                work["price"]["max"] = min(round(float(work["price"]["max"]) * 1.2, 2), round(orig * 2.0, 2))
                relaxed.append("price_max+20%")
            elif step == "price_min" and work["price"].get("min") is not None:
                work["price"]["min"] = round(float(work["price"]["min"]) * 0.8, 2)
                relaxed.append("price_min-20%")
            else:
                continue
        elif step in work.get("must", {}):
            del work["must"][step]
            relaxed.append(step)
        else:
            continue
        ok = [p for p in catalog if matches(p, work)[0]]
    return ok, relaxed
