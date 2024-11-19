# API

Base: `http://localhost:8000`. OpenAPI at `/docs`.

## POST /api/v1/search
Body: `{query, limit=20, category?}` → `{query, parsed, hits[], total, relaxed[]}`.
Hit: `{id, title, brand, category, price, currency, url, image, rating, match_score, explanation{matched,partial,missing}}`.

## GET /api/v1/products/{id}
Full card with `specs{}` and description.

## GET /api/v1/suggest?q=
Prefix suggestions (brands + titles, max 10).

## POST /api/v1/feedback
`{query, product_id, event, rating?}` → `{ok, logged}`. Also writes `search_logs`.

## POST /api/v1/admin/reindex
Header `X-API-Key: $ADMIN_API_KEY`. Rebuilds keyword + vector indexes.

## GET /api/v1/health
`{status, service, env, reranker, llm_provider}`. Rate limit 60/min/IP, `X-Request-ID` on all responses.
