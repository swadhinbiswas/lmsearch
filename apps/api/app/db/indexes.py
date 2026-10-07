"""Index + HNSW tuning notes (applied in migration 0002).

- embeddings HNSW: m=16, ef_construction=64; query time ef_search=40.
- specs GIN: to_tsvector(title) for keyword prefilter.
- price B-tree for range filters; (key, value_num) composite for spec filters.
p95 targets: <800ms cached, <2s cold (measured in docs/ranking.md).
"""

HNSW_M = 16
HNSW_EF_CONSTRUCTION = 64
HNSW_EF_SEARCH = 40
RRF_K = 60
HYBRID_PREFETCH = 100
RERANK_TOP = 50
