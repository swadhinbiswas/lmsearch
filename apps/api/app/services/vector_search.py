"""Vector similarity search: pgvector (HNSW) when DB reachable, in-memory cosine fallback."""
from __future__ import annotations

import math

from apps.api.app.services.embedder import embed_one
from apps.api.app.services.text_utils import product_text

_mem_vectors: dict[int, list[float]] = {}
_prod_vec_cache: dict[int, list[float]] = {}


def _vec_for(pid: int, text: str) -> list[float]:
    v = _mem_vectors.get(pid) or _prod_vec_cache.get(pid)
    if v is None:
        v = embed_one(text)
        _prod_vec_cache[pid] = v
    return v


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def index_vectors(docs: list[dict]) -> int:
    for d in docs:
        _mem_vectors[int(d["id"])] = embed_one(product_text(d))
    # Best-effort pgvector upsert (skipped when DB unavailable)
    try:
        from apps.api.app.db.session import SessionLocal  # type: ignore
        from sqlalchemy import text as sqltext  # type: ignore

        db = SessionLocal()
        try:
            for d in docs:
                vec = _mem_vectors[int(d["id"])]
                lit = "[" + ",".join(f"{v:.6f}" for v in vec) + "]"
                db.execute(
                    sqltext(
                        "INSERT INTO product_embeddings (product_id, embedding, text_hash) "
                        "VALUES (:pid, :emb::vector(384), :h) "
                        "ON CONFLICT (product_id) DO UPDATE SET embedding=:emb::vector(384)"
                    ),
                    {"pid": int(d["id"]), "emb": lit, "h": "mem"},
                )
            db.commit()
        finally:
            db.close()
    except Exception:
        pass
    return len(docs)


def vector_search(query: str, docs: list[dict] | None = None, limit: int = 100) -> list[tuple[int, float]]:
    qv = embed_one(query)
    # Try pgvector first
    try:
        from apps.api.app.db.session import SessionLocal  # type: ignore
        from sqlalchemy import text as sqltext  # type: ignore

        db = SessionLocal()
        try:
            lit = "[" + ",".join(f"{v:.6f}" for v in qv) + "]"
            rows = db.execute(
                sqltext(
                    "SELECT product_id, 1 - (embedding <=> :q::vector(384)) AS score "
                    "FROM product_embeddings ORDER BY embedding <=> :q::vector(384) LIMIT :lim"
                ),
                {"q": lit, "lim": limit},
            ).fetchall()
            if rows:
                return [(int(r[0]), float(r[1])) for r in rows]
        finally:
            db.close()
    except Exception:
        pass
    # In-memory fallback
    pool = docs if docs is not None else []
    if docs is None and _mem_vectors:
        scored = [(pid, cosine(qv, v)) for pid, v in _mem_vectors.items()]
        scored.sort(key=lambda x: -x[1])
        return scored[:limit]
    if not pool:
        from apps.api.app.services.catalog import load_catalog

        pool = load_catalog()
    scored = [(int(d["id"]), cosine(qv, _vec_for(int(d["id"]), product_text(d)))) for d in pool]
    scored.sort(key=lambda x: -x[1])
    return scored[:limit]
