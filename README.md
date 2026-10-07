<div align="center">
  <img src="apps/web/public/mascot.svg" alt="lmsearch mascot" width="120" />
</div>

# lmsearch — natural-language product search

> Rebuilt from the original 2024 lmsearch project; commit dates reflect the original development timeline.

Type a plain request such as *"Ryzen laptop with 32GB RAM under $1200 for programming"* or
*"gaming phone, 120Hz screen, 5000mAh battery, below 40k BDT"* and get ranked product
cards with a per-product explanation of what matched.

The demo catalog holds 96 real 2024 laptop and phone models with their true specs.
40 of them carry verified product photos; the rest show a placeholder until a photo
is curated. Prices are indicative 2024 street prices, not live quotes.

## Run it

```bash
cp .env.example .env        # set OPENAI_API_KEY (optional) and ADMIN_API_KEY
make up                     # postgres + redis + meilisearch + api on :8000
make seed                   # load the 96-product catalog
make reindex                # build keyword + vector indexes
cd apps/web && npm install && npm run dev   # storefront on :3000
```

Without an `OPENAI_API_KEY` the parser runs fully offline: the deterministic
rule layer handles RAM, storage, CPU, brands, prices (`k`/`lakh`/BDT/`৳`,
under/below/around/between) and Bangla-English mixed queries. Set
`LMSEARCH_USE_HF_EMBEDDINGS=1` / `LMSEARCH_USE_HF_RERANKER=1` to use the real
bge models; otherwise the services fall back to deterministic local scoring.

```bash
curl -X POST localhost:8000/api/v1/search -H 'Content-Type: application/json' \
  -d '{"query":"Ryzen laptop 32GB RAM under $1200","limit":5}'
```

## How a query flows

```
query → LLM parse (gpt-4o-mini, 2s timeout) + rule repair → hard spec filters
      → Meilisearch top-100 + pgvector top-100 in parallel → RRF fusion (k=60)
      → cross-encoder rerank top-50 → composite score → explanation
```

`score = 0.5·rerank + 0.2·spec_match + 0.15·price_fit + 0.1·rating + 0.05·freshness`.
Fewer than 5 hits triggers progressive relaxation (brand, then price ±20%, then
refresh/battery, storage, RAM, CPU) and the response reports what was relaxed.
Details: `docs/architecture.md`, `docs/ranking.md`, `docs/api.md`.

## Measured quality

100-query eval set (`ml/eval/dataset.json`, `python ml/evaluate.py`):

- Parser spec-accuracy: **1.000** (CI fails below 0.90)
- Precision@10: **0.952** · nDCG@10: **0.943**
- API tests: 20 passed; `ruff check` and `black --check` clean

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/search` | Ranked hits with `parsed`, `relaxed[]`, explanations |
| GET | `/api/v1/products/{id}` | Full card with specs |
| GET | `/api/v1/suggest?q=` | Prefix suggestions |
| POST | `/api/v1/feedback` | Click/rating log |
| POST | `/api/v1/admin/reindex` | Rebuild indexes (`X-API-Key` required) |
| GET | `/api/v1/health` | Service status |

Interactive docs at `/docs`. Rate limit is 60 requests/min per IP; every
response carries an `X-Request-ID`.

## Roadmap

- [ ] Sellers for the BD market with live price refresh
- [ ] Price-drop alerts from `search_logs`
- [ ] Bangla-language embeddings
- [ ] Kubernetes manifests and a staging environment
