"""Search: parse (cached) → filters → hybrid → rerank → composite → explain (cached)."""

import time

from fastapi import APIRouter

from apps.api.app.core.cache import cache_get, cache_set
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
    norm = body.query.strip().lower()
    cache_key_raw = f"{norm}|{body.category}|{body.limit}"
    cached = cache_get("search", cache_key_raw)
    if cached:
        return SearchResponse(**cached)
    parsed_cached = cache_get("parsed", norm)
    if parsed_cached:
        parsed = parsed_cached
    else:
        parsed = parse_query_multilingual(body.query)
        cache_set("parsed", norm, parsed, ttl_s=3600)
    if body.category and not parsed.get("category"):
        parsed["category"] = body.category
    catalog = load_catalog()
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
            continue
        spec_s, expl = spec_match_score(p, parsed)
        ps = price_fit_score(p, parsed)
        final = composite_score(rr.get(pid, 0.0), spec_s, ps, float(p.get("rating", 0)))
        card = to_hit(p, final)
        card["explanation"] = expl
        hits.append(ProductHit(**card))
        if len(hits) >= body.limit:
            break
    hits.sort(key=lambda h: -h.match_score)
    resp = SearchResponse(query=body.query, parsed=parsed, hits=hits, total=len(hits), relaxed=relaxed)
    cache_set("search", cache_key_raw, resp.model_dump(), ttl_s=300)
    _ = int((time.time() - t0) * 1000)
    return resp
