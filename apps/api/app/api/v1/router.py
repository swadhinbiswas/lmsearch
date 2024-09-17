from fastapi import APIRouter

from apps.api.app.api.v1.admin import router as admin_router
from apps.api.app.api.v1.feedback import router as feedback_router
from apps.api.app.api.v1.health import router as health_router
from apps.api.app.api.v1.products import router as products_router
from apps.api.app.api.v1.search import router as search_router
from apps.api.app.api.v1.suggest import router as suggest_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(search_router, tags=["search"])
api_router.include_router(products_router, tags=["products"])
api_router.include_router(suggest_router, tags=["suggest"])
api_router.include_router(feedback_router, tags=["feedback"])
api_router.include_router(admin_router, tags=["admin"])
