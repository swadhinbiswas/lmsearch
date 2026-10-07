"""Cross-encoder reranker (bge-reranker-base) with lexical fallback.

Toggle with ENABLE_RERANKER=false. Fallback = token-overlap score in [0,1].
"""

from __future__ import annotations

_model = None


def _load():
    global _model
    if _model is not None:
        return _model
    try:
        import os

        from apps.api.app.core.config import get_settings

        if not get_settings().enable_reranker:
            return None
        if os.getenv("LMSEARCH_USE_HF_RERANKER", "0") != "1":
            return None
        from sentence_transformers import CrossEncoder  # type: ignore

        _model = CrossEncoder(get_settings().reranker_model)
        return _model
    except Exception:
        return None


def _lexical_score(query: str, doc: str) -> float:
    q = set(query.lower().split())
    d = set(doc.lower().split())
    if not q:
        return 0.0
    return len(q & d) / len(q)


def rerank(query: str, docs: list[dict], top_k: int = 50) -> list[tuple[int, float]]:
    texts = [f"{d.get('title','')} {d.get('description','')}" for d in docs]
    model = _load()
    scores: list[float] = []
    if model is not None:
        try:
            pairs = [[query, t] for t in texts]
            raw = model.predict(pairs)
            # squash to [0,1] via sigmoid
            import math

            scores = [1 / (1 + math.exp(-float(s))) for s in raw]
        except Exception:
            scores = [_lexical_score(query, t) for t in texts]
    else:
        scores = [_lexical_score(query, t) for t in texts]
    ranked = sorted(zip([int(d["id"]) for d in docs], scores, strict=False), key=lambda x: -x[1])
    return ranked[:top_k]
