"""Search schemas v0 (extended in later nlp phases)."""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=20, ge=1, le=50)
    category: str | None = None


class ProductHit(BaseModel):
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
    explanation: dict = {}


class SearchResponse(BaseModel):
    query: str
    parsed: dict = {}
    hits: list[ProductHit] = []
    total: int = 0
    relaxed: list[str] = []
