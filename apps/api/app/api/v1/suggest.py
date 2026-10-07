"""Prefix suggestions from brands + titles (no external service)."""

from apps.api.app.services.catalog import load_catalog
from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/suggest")
def suggest(q: str = Query(default="", min_length=1, max_length=100)) -> dict:
    catalog = load_catalog()
    low = q.lower().strip()
    out: list[str] = []
    for p in catalog:
        t = p["title"]
        if low in t.lower() and t not in out:
            out.append(t)
        if len(out) >= 8:
            break
    brands = sorted({p["brand"] for p in catalog if p["brand"].lower().startswith(low)})
    return {"query": q, "suggestions": (brands[:3] + out)[:10]}
