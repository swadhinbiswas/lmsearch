"""Central application settings (pydantic-settings, 12-factor)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "lmsearch"
    env: str = "dev"
    database_url: str = "postgresql+psycopg://lmsearch:lmsearch@localhost:5432/lmsearch"
    redis_url: str = "redis://localhost:6379/0"
    meili_host: str = "http://localhost:7700"
    meili_master_key: str = "local-dev-key"
    openai_api_key: str = ""
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_timeout_s: float = 2.0
    admin_api_key: str = "change-me"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    reranker_model: str = "BAAI/bge-reranker-base"
    enable_reranker: bool = True
    rrf_k: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
