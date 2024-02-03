# lmsearch — AI Natural-Language Product Search Engine

> Rebuilt from the original 2024 lmsearch project; commit dates reflect the original development timeline.

Type a free-form request like *"Ryzen laptop with 32GB RAM under $1200 for programming"* or
*"gaming phone, 120Hz screen, 5000mAh battery, below 40k BDT"* and get ranked product cards
with match explanations.

- Hybrid retrieval: PostgreSQL hard filters + Meilisearch keyword + pgvector semantic → RRF fusion → cross-encoder rerank → composite scoring.
- LLM query parser (OpenAI `gpt-4o-mini` with pluggable provider, Ollama/Llama 3 fallback) + deterministic regex repair layer.
- 500+ seeded products, eval harness (Precision@10 / nDCG@10), Next.js storefront, Docker Compose stack.

See `docs/architecture.md`, `docs/ranking.md`, `docs/api.md`. Quick start: `make up`.
