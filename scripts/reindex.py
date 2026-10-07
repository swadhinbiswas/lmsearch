"""Reindex helper (v0): loads seed catalog into keyword index."""

from __future__ import annotations

import sys

sys.path.insert(0, "apps/api")
sys.path.insert(0, ".")

from apps.api.app.services.keyword_search import index_products  # noqa: E402
from scripts.seed_data import gen_products  # noqa: E402


def main() -> None:
    docs = gen_products(600)
    n = index_products(
        [
            {
                "id": p["id"],
                "title": p["title"],
                "description": p["description"],
                "brand": p["brand"],
            }
            for p in docs
        ]
    )
    print(f"indexed {n} products")


if __name__ == "__main__":
    main()
