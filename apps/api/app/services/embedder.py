"""Embedding service: bge-small-en-v1.5 (384d) with deterministic hash fallback.

Heavy deps (sentence-transformers/torch) are optional at import time so unit
tests and CI stay fast. Set EMBEDDING_MODEL=BAAI/bge-small-en-v1.5 in prod.
"""
from __future__ import annotations

import hashlib
import math
from functools import lru_cache

DIM = 384
_model = None


def _hf_enabled() -> bool:
    import os

    return os.getenv("LMSEARCH_USE_HF_EMBEDDINGS", "0") == "1"


def _load_model():
    global _model
    if _model is not None:
        return _model
    if not _hf_enabled():
        return None
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore

        from apps.api.app.core.config import get_settings

        _model = SentenceTransformer(get_settings().embedding_model)
        return _model
    except Exception:
        return None


def hash_embed(text: str, dim: int = DIM) -> list[float]:
    """Deterministic char-ngram hash embedding, L2-normalized."""
    vec = [0.0] * dim
    toks = (text or "").lower().split()
    for tok in toks:
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        for i in range(3):
            vec[(h >> (i * 10)) % dim] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def embed(texts: str | list[str]) -> list[list[float]]:
    single = isinstance(texts, str)
    batch = [texts] if single else list(texts)
    # Prefix improves bge retrieval quality
    prefixed = [f"Represent this sentence for searching relevant passages: {t}" for t in batch]
    model = _load_model()
    if model is not None:
        try:
            import numpy as np  # type: ignore

            arr = model.encode(prefixed, normalize_embeddings=True)
            return [list(map(float, row)) for row in arr]
        except Exception:
            pass
    return [hash_embed(t) for t in batch]


def embed_one(text: str) -> list[float]:
    return embed(text)[0]


@lru_cache(maxsize=4096)
def embed_cached(text: str) -> tuple[float, ...]:
    return tuple(embed_one(text))
