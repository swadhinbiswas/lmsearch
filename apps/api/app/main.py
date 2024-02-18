"""FastAPI entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.app.api.v1.health import router as health_router
from apps.api.app.core.logging import setup_logging

setup_logging()


def create_app() -> FastAPI:
    app = FastAPI(title="lmsearch", version="0.1.0", docs_url="/docs", openapi_url="/openapi.json")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router, prefix="/api/v1", tags=["health"])
    app.include_router(health_router, tags=["health-root"])

    @app.get("/health")
    def root_health() -> dict:
        return {"status": "ok", "service": "lmsearch-api"}

    return app


app = create_app()
