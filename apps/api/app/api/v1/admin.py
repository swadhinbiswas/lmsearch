"""Admin routes (API-key protected)."""

from apps.api.app.core.security import require_admin
from apps.api.app.services import keyword_search as ks
from apps.api.app.services import vector_search as vs
from apps.api.app.services.catalog import load_catalog
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/admin/reindex")
def reindex(_: None = Depends(require_admin)) -> dict:
    catalog = load_catalog()
    kw_docs = [
        {
            "id": p["id"],
            "title": p["title"],
            "description": p.get("description", ""),
            "brand": p.get("brand", ""),
        }
        for p in catalog
    ]
    ks.index_products(kw_docs)
    vs.index_vectors(catalog)
    return {"ok": True, "indexed": len(catalog)}
