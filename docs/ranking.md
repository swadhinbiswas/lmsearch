# Ranking

Pipeline: parse → SQL hard filters → Meilisearch top-100 + pgvector top-100 (parallel) → RRF(k=60) → rerank top-50 → composite.

## RRF
`score(pid) = Σ 1/(60 + rank_i)` over keyword and vector lists.

## Composite
`score = 0.5*rerank + 0.2*spec_match + 0.15*price_fit + 0.1*rating + 0.05*freshness`
- rerank: cross-encoder sigmoid in [0,1] (lexical overlap fallback).
- spec_match: fraction of `must` clauses fully met (partial credit 0.5 for near RAM).
- price_fit: 1.0 inside [min,max], linear decay outside.
- rating: `(rating-3)/2` clipped; freshness constant 0.5 on seed data.

## Relaxation
If <5 results, drop in order: brand → price±20% → refresh/battery → storage → ram → cpu.
Every relaxation is reported in `relaxed[]` and shown as dashed chips in the UI.

## Targets
p95 <800ms cached, <2s cold. Eval: Precision@10 0.952, nDCG@10 0.943, parser accuracy 100% (gate ≥90%).
