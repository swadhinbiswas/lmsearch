"""Search: parse → filters → hybrid → rerank → composite score → explain."""

import time

from fastapi import APIRouter

from apps.api.app.schemas.search import ProductHit, SearchRequest, SearchResponse
from apps.api.app.services.catalog import load_catalog, to_hit
from apps.api.app.services.explainer import composite_score, price_fit_score, spec_match_score
from apps.api.app.services.filters import apply_filters
from apps.api.app.services.hybrid import hybrid_search
from apps.api.app.services.query_parser_bn import parse_query_multilingual
from apps.api.app.services.reranker import rerank

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search(body: SearchRequest) -> SearchResponse:
    t0 = time.time()
    catalog = load_catalog()
    parsed = parse_query_multilingual(body.query)
    if body.category and not parsed.get("category"):
        parsed["category"] = body.category
    filtered, relaxed = apply_filters(catalog, parsed)
    pool = filtered if filtered else catalog
    ranked = hybrid_search(parsed.get("semantic_query") or body.query, docs=pool, limit=100)
    by_id = {p["id"]: p for p in pool}
    if filtered:
        fids = {p["id"] for p in filtered}
        ranked = [(pid, s) for pid, s in ranked if pid in fids]
    top_docs = [by_id[pid] for pid, _ in ranked[:50] if pid in by_id]
    rr = dict(rerank(parsed.get("semantic_query") or body.query, top_docs, top_k=50))
    hits: list[ProductHit] = []
    for pid, _ in ranked[:50]:
        p = by_id.get(pid)
        if p is None:
            break
        spec_s, expl = spec_match_score(p, parsed)
        ps = price_fit_score(p, parsed)
        final = composite_score(rr.get(pid, 0.0), spec_s, ps, float(p.get("rating", 0)))
        card = to_hit(p, final)
        card["explanation"] = expl
        hits.append(ProductHit(**card))
        if len(hits) >= body.limit:
            break
    hits.sort(key=lambda h: -h.match_score)
    _ = int((time.time() - t0) * 1000)
    return SearchResponse(query=body.query, parsed=parsed, hits=hits, total=len(hits), relaxed=relaxed)
