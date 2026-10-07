"""Feedback + search logs (DB best-effort, in-memory always)."""

import time

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
_logs: list[dict] = []


class FeedbackIn(BaseModel):
    query: str = ""
    product_id: int | None = None
    event: str = "click"
    rating: int | None = None


@router.post("/feedback")
def feedback(body: FeedbackIn) -> dict:
    entry = {
        "query": body.query,
        "product_id": body.product_id,
        "event": body.event,
        "rating": body.rating,
        "ts": time.time(),
    }
    _logs.append(entry)
    try:
        from apps.api.app.db.models import SearchLog  # type: ignore
        from apps.api.app.db.session import SessionLocal  # type: ignore
        from sqlalchemy.exc import SQLAlchemyError  # type: ignore

        db = SessionLocal()
        try:
            db.add(
                SearchLog(
                    raw_query=body.query,
                    parsed_json={"event": body.event},
                    latency_ms=0,
                    result_count=0,
                    clicked_product_id=body.product_id,
                )
            )
            db.commit()
        except SQLAlchemyError:
            db.rollback()
        finally:
            db.close()
    except Exception:
        pass
    return {"ok": True, "logged": len(_logs)}


@router.get("/feedback/stats")
def feedback_stats() -> dict:
    return {"total": len(_logs)}
