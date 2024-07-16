"""Composite scoring + per-product explanations.

score = 0.5*rerank + 0.2*spec_match + 0.15*price_fit + 0.1*rating + 0.05*freshness
explainer -> {matched[], partial[], missing[]}
"""
from __future__ import annotations


def spec_match_score(p: dict, parsed: dict) -> tuple[float, dict]:
    must = parsed.get("must", {}) or {}
    matched, partial, missing = [], [], []
    if not must:
        return 0.5, {"matched": matched, "partial": partial, "missing": missing}
    total = len(must)
    full = 0.0
    specs = p.get("specs", {})
    labels = {
        "ram_gb_min": f"{specs.get('ram_gb','?')}GB RAM",
        "storage_gb_min": f"{specs.get('storage_gb','?')}GB storage",
        "cpu_series": f"CPU {specs.get('cpu_model', specs.get('chipset','?'))}",
        "refresh_hz_min": f"{specs.get('refresh_hz','?')}Hz screen",
        "battery_mah_min": f"{specs.get('battery_mah','?')}mAh battery",
    }
    for k, want in must.items():
        label = labels.get(k, k)
        if k == "ram_gb_min":
            have = specs.get("ram_gb", 0) or 0
            if have >= want:
                matched.append(f"{have}GB RAM meets {want}GB required")
                full += 1
            elif have >= want * 0.75:
                partial.append(f"{have}GB RAM close to {want}GB")
                full += 0.5
            else:
                missing.append(f"needs {want}GB RAM, has {have}GB")
        elif k == "storage_gb_min":
            have = specs.get("storage_gb", 0) or 0
            if have >= want:
                matched.append(f"{have}GB storage meets {want}GB required")
                full += 1
            else:
                missing.append(f"needs {want}GB storage, has {have}GB")
        elif k == "cpu_series":
            blob = f"{specs.get('cpu_brand','')} {specs.get('cpu_model','')} {specs.get('chipset','')}".lower()
            if any(str(w).lower() in blob for w in (want or [])):
                matched.append(f"CPU matches {'/'.join(want)}")
                full += 1
            else:
                missing.append(f"CPU {blob.strip() or 'unknown'} not in {'/'.join(want)}")
        elif k == "refresh_hz_min":
            have = specs.get("refresh_hz", 0) or 0
            if have >= want:
                matched.append(f"{have}Hz screen meets {want}Hz")
                full += 1
            else:
                missing.append(f"needs {want}Hz, has {have}Hz")
        elif k == "battery_mah_min":
            have = specs.get("battery_mah", 0) or 0
            if have >= want:
                matched.append(f"{have}mAh battery meets {want}mAh")
                full += 1
            else:
                missing.append(f"needs {want}mAh, has {have}mAh")
        else:
            matched.append(label)
            full += 1
    # brand / price notes
    brands = parsed.get("brands") or []
    if brands:
        if p.get("brand", "").lower() in [b.lower() for b in brands]:
            matched.append(f"brand {p.get('brand')} matches")
        else:
            missing.append(f"brand {p.get('brand')} not in {brands}")
    price = parsed.get("price") or {}
    if price.get("max") is not None:
        if float(p.get("price", 0)) <= float(price["max"]):
            matched.append(f"${float(p.get('price',0)):.0f} within budget ${float(price['max']):.0f}")
        else:
            missing.append(f"${float(p.get('price',0)):.0f} over budget ${float(price['max']):.0f}")
    return round(full / max(1, total), 4), {"matched": matched, "partial": partial, "missing": missing}


def price_fit_score(p: dict, parsed: dict) -> float:
    price = parsed.get("price") or {}
    if price.get("max") is None and price.get("min") is None:
        return 0.5
    val = float(p.get("price", 0))
    mx = price.get("max")
    mn = price.get("min")
    if mx is not None and mn is not None and mx > mn:
        if mn <= val <= mx:
            return 1.0
        return max(0.0, 1 - min(abs(val - mx), abs(val - mn)) / (mx - mn + 1))
    if mx is not None:
        return 1.0 if val <= mx else max(0.0, 1 - (val - mx) / (mx + 1))
    if mn is not None:
        return 1.0 if val >= mn else max(0.0, val / (mn + 1))
    return 0.5


def composite_score(rerank_s: float, spec_s: float, price_s: float, rating: float) -> float:
    rating_s = max(0.0, min(1.0, (rating - 3.0) / 2.0))
    freshness = 0.5  # seed catalog has no age signal; constant keeps formula stable
    return round(0.5 * rerank_s + 0.2 * spec_s + 0.15 * price_s + 0.1 * rating_s + 0.05 * freshness, 4)
