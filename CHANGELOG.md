# Changelog

## v1.0.0 (2024-12-22)
- Hybrid retrieval (Meilisearch + pgvector + RRF k=60) with cross-encoder rerank and composite scoring.
- LLM structured query parser (gpt-4o-mini, Ollama fallback) + rule repair; BDT/USD/৳, k/lakh, Bangla-English.
- Hard spec filters + progressive relaxation with explanations.
- Next.js storefront: understood-as chips, facets, product page, compare, dark mode.
- Eval harness (100 queries), CI, rate limiting, request IDs, Docker Compose stack.
