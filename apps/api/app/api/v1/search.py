"""Search: hybrid RRF (keyword + vector). Filters/rerank land in later phases."""

from fastapi import APIRouter

from apps.api.app.schemas.search import ProductHit, SearchRequest, SearchResponse
from apps.api.app.services.catalog import load_catalog, to_hit
from apps.api.app.services.hybrid import hybrid_search

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search_hybrid(body: SearchRequest) -> SearchResponse:
    catalog = load_catalog()
    if body.category:
        catalog = [p for p in catalog if p.get("category") == body.category]
    ranked = hybrid_search(body.query, docs=catalog, limit=body.limit)
    by_id = {p["id"]: p for p in catalog}
    hits = [ProductHit(**to_hit(by_id[pid], score)) for pid, score in ranked[: body.limit] if pid in by_id]
    return SearchResponse(query=body.query, parsed={"mode": "hybrid-rrf"}, hits=hits, total=len(hits))
