"""Search: parse → hard filters → hybrid → relaxation report."""

from fastapi import APIRouter

from apps.api.app.schemas.search import ProductHit, SearchRequest, SearchResponse
from apps.api.app.services.catalog import load_catalog, to_hit
from apps.api.app.services.filters import apply_filters
from apps.api.app.services.hybrid import hybrid_search
from apps.api.app.services.query_parser_bn import parse_query_multilingual

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search(body: SearchRequest) -> SearchResponse:
    catalog = load_catalog()
    parsed = parse_query_multilingual(body.query)
    if body.category and not parsed.get("category"):
        parsed["category"] = body.category
    filtered, relaxed = apply_filters(catalog, parsed)
    pool = filtered if filtered else catalog
    query_text = parsed.get("semantic_query") or body.query
    ranked = hybrid_search(query_text, docs=pool, limit=max(body.limit * 3, 50))
    by_id = {p["id"]: p for p in pool}
    # keep only filtered ids when filters matched something
    if filtered:
        fids = {p["id"] for p in filtered}
        ranked = [(pid, s) for pid, s in ranked if pid in fids]
    hits = [ProductHit(**to_hit(by_id[pid], score)) for pid, score in ranked[: body.limit] if pid in by_id]
    return SearchResponse(query=body.query, parsed=parsed, hits=hits, total=len(hits), relaxed=relaxed)
