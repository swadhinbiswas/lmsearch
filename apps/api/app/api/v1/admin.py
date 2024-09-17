"""Admin routes (API-key protected)."""

from fastapi import APIRouter, Header, HTTPException

from apps.api.app.core.config import get_settings
from apps.api.app.services import keyword_search as ks
from apps.api.app.services import vector_search as vs
from apps.api.app.services.catalog import load_catalog

router = APIRouter()


def _check(key: str | None) -> None:
    if key != get_settings().admin_api_key:
        raise HTTPException(status_code=401, detail="invalid admin key")


@router.post("/admin/reindex")
def reindex(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> dict:
    _check(x_api_key)
    catalog = load_catalog()
    kw_docs = [{"id": p["id"], "title": p["title"], "description": p.get("description", ""), "brand": p.get("brand", "")} for p in catalog]
    ks.index_products(kw_docs)
    vs.index_vectors(catalog)
    return {"ok": True, "indexed": len(catalog)}
