"""Bangla-English + currency-aware wrapper over the rule parser."""

from apps.api.app.services import currency as cur
from apps.api.app.services import query_parser as base


def parse_query_multilingual(q: str) -> dict:
    norm = cur.transliterate_mixed(q)
    parsed = base.parse_query_rule(norm)
    price = cur.parse_price(q)
    if price:
        # catalog prices are USD; filter on converted bound
        usd_max = price.get("max_usd", price.get("max"))
        usd_min = price.get("min_usd", price.get("min"))
        parsed["price"] = {
            "min": usd_min,
            "max": usd_max,
            "currency": "USD",
            "original": {
                "min": price.get("min"),
                "max": price.get("max"),
                "currency": price.get("currency"),
            },
        }
    # re-detect category on transliterated text (catches ল্যাপটপ/ফোন)
    cat = base.detect_category(norm)
    if cat:
        parsed["category"] = cat
    parsed["semantic_query"] = q.strip()
    return parsed
