"""In-memory catalog used when Postgres is unavailable (dev/tests)."""
from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=1)
def load_catalog(n: int = 600) -> list[dict]:
    from scripts.seed_data import gen_products

    return gen_products(n)


def to_hit(p: dict, score: float = 0.0) -> dict:
    img = (p.get("image_urls") or [""])[0] if p.get("image_urls") else ""
    return {
        "id": p["id"],
        "title": p["title"],
        "brand": p.get("brand", ""),
        "category": p.get("category", ""),
        "price": float(p.get("price", 0)),
        "currency": p.get("currency", "USD"),
        "url": p.get("url", ""),
        "image": img,
        "rating": float(p.get("rating", 0)),
        "match_score": round(float(score), 4),
        "explanation": {"matched": [], "partial": [], "missing": []},
    }
