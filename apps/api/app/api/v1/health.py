from fastapi import APIRouter

from apps.api.app.core.config import get_settings

router = APIRouter()


@router.get("/health")
def health() -> dict:
    s = get_settings()
    return {
        "status": "ok",
        "service": "lmsearch-api",
        "env": s.env,
        "reranker": s.enable_reranker,
        "llm_provider": s.llm_provider,
    }
