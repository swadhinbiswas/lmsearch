# Architecture

```mermaid
flowchart LR
    U[User query] --> P[Query parser: LLM gpt-4o-mini + rule repair + cache]
    P --> F[Hard spec filters: SQL on products/specs + price]
    F --> K[Meilisearch top 100]
    F --> V[pgvector HNSW top 100]
    K --> RRF[RRF fusion k=60]
    V --> RRF
    RRF --> R[Cross-encoder rerank top 50]
    R --> S[Composite score 0.5/0.2/0.15/0.1/0.05]
    S --> E[Explainer matched/partial/missing]
    E --> C[Redis cache + API]
    C --> W[Next.js storefront]
```

## Services
- `apps/api/app/services/query_parser.py` rule layer; `llm_parser.py` provider interface (openai/ollama, 2s timeout, fallback).
- `spec_normalizer.py` shared with ingest; `currency.py` k/lakh/BDT/৳; `query_parser_bn.py` Bangla-English.
- `keyword_search.py` Meilisearch + in-memory fallback; `vector_search.py` pgvector HNSW + cosine fallback.
- `hybrid.py` parallel fetch + RRF; `reranker.py` bge-reranker-base toggle; `explainer.py` composite scoring.
- `filters.py` hard filters + progressive relaxation (brand → price+20% → refresh/battery → storage → ram → cpu).
- `catalog.py` seed catalog (600 products) when Postgres is absent; `core/cache.py` Redis + LRU.

## Data
PostgreSQL 16 + pgvector (`vector(384)`, HNSW m=16/ef=64), GIN on title, B-tree on price, composite (key, value_num).
Meilisearch `products` index; Redis for parsed-query (1h) and result (5min) caches.
