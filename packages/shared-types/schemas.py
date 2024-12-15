"""Python mirror of the TypeScript shared types (import-light, pydantic-free)."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ProductHit:
    id: int
    title: str
    brand: str = ""
    category: str = ""
    price: float = 0
    currency: str = "USD"
    url: str = ""
    image: str = ""
    rating: float = 0.0
    match_score: float = 0.0
