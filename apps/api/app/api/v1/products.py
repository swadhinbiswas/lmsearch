"""Product detail endpoint (DB when available, catalog fallback)."""

from apps.api.app.services.catalog import load_catalog, to_hit
from apps.api.app.services.explainer import spec_match_score
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/products/{product_id}")
def get_product(product_id: int) -> dict:
    catalog = load_catalog()
    hit = next((p for p in catalog if p["id"] == product_id), None)
    if hit is None:
        raise HTTPException(status_code=404, detail="product not found")
    card = to_hit(hit, 1.0)
    card["specs"] = hit.get("specs", {})
    card["description"] = hit.get("description", "")
    _, expl = spec_match_score(hit, {"must": {}, "brands": [], "price": {}})
    card["explanation"] = expl
    return card
