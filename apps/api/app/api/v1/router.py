from fastapi import APIRouter

from apps.api.app.api.v1.health import router as health_router
from apps.api.app.api.v1.search import router as search_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(search_router, tags=["search"])
