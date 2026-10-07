"""Keyword search: Meilisearch when reachable, in-memory fallback otherwise.

The fallback keeps `make up` / CI green without external services and is the
code path exercised by unit tests.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_WORD = re.compile(r"[a-z0-9৳]+", re.I)


def tokenize(text: str) -> list[str]:
    return _WORD.findall((text or "").lower())


@dataclass
class KeywordIndex:
    docs: list[dict]

    def add_documents(self, docs: list[dict]) -> None:
        self.docs = list(docs)

    def search(self, query: str, limit: int = 100) -> list[tuple[int, float]]:
        qtok = set(tokenize(query))
        scored: list[tuple[int, float]] = []
        for d in self.docs:
            blob = f"{d.get('title','')} {d.get('description','')} {d.get('brand','')}"
            dtok = set(tokenize(blob))
            if not qtok or not dtok:
                continue
            overlap = len(qtok & dtok) / max(1, len(qtok))
            # title matches weigh more
            title_tok = set(tokenize(d.get("title", "")))
            title_overlap = len(qtok & title_tok) / max(1, len(qtok))
            score = 0.6 * title_overlap + 0.4 * overlap
            if score > 0:
                scored.append((int(d["id"]), score))
        scored.sort(key=lambda x: -x[1])
        return scored[:limit]


_mem_index = KeywordIndex(docs=[])


def get_index() -> KeywordIndex:
    return _mem_index


def try_meili_search(query: str, limit: int = 100) -> list[tuple[int, float]] | None:
    """Attempt a real Meilisearch query; return None when unconfigured/unreachable."""
    try:
        import meilisearch  # type: ignore
        from apps.api.app.core.config import get_settings

        s = get_settings()
        if not s.meili_host:
            return None
        client = meilisearch.Client(s.meili_host, s.meili_master_key)
        res = client.index("products").search(query, {"limit": limit})
        out = []
        for h in res.get("hits", []):
            pid = h.get("id")
            if pid is not None:
                out.append((int(pid), float(h.get("_rankingScore", 0.5))))
        return out
    except Exception:
        return None


def keyword_search(
    query: str, docs: list[dict] | None = None, limit: int = 100
) -> list[tuple[int, float]]:
    live = try_meili_search(query, limit)
    if live is not None and live:
        return live
    idx_docs = docs if docs is not None else _mem_index.docs
    if docs is not None:
        return KeywordIndex(docs=idx_docs).search(query, limit)
    return _mem_index.search(query, limit)


def index_products(docs: list[dict]) -> int:
    _mem_index.add_documents(docs)
    try:
        import meilisearch  # type: ignore
        from apps.api.app.core.config import get_settings

        s = get_settings()
        client = meilisearch.Client(s.meili_host, s.meili_master_key)
        client.index("products").add_documents(docs)
    except Exception:
        pass
    return len(docs)
