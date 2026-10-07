"""SQLAlchemy engine/session helpers."""

from apps.api.app.core.config import get_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


def get_engine(echo: bool = False):
    settings = get_settings()
    return create_engine(settings.database_url, echo=echo, pool_pre_ping=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
