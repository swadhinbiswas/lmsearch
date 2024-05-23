"""Hybrid retrieval: parallel keyword + vector, fused with RRF (k=60)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from apps.api.app.services import keyword_search as ks
from apps.api.app.services import vector_search as vs


def rrf_fuse(rank_lists: list[list[tuple[int, float]]], k: int = 60) -> list[tuple[int, float]]:
    scores: dict[int, float] = {}
    for ranked in rank_lists:
        for rank, (pid, _s) in enumerate(ranked, start=1):
            scores[pid] = scores.get(pid, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])


def hybrid_search(
    query: str,
    docs: list[dict] | None = None,
    limit: int = 100,
    rrf_k: int = 60,
) -> list[tuple[int, float]]:
    with ThreadPoolExecutor(max_workers=2) as ex:
        f_kw = ex.submit(ks.keyword_search, query, docs, limit)
        f_v = ex.submit(vs.vector_search, query, docs, limit)
        kw = f_kw.result()
        vv = f_v.result()
    return rrf_fuse([kw, vv], k=rrf_k)[:limit]
