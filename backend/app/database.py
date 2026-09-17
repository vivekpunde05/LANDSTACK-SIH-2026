from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings

database_url = get_settings().database_url
engine = create_engine(database_url, pool_pre_ping=True, connect_args={"connect_timeout": 2}) if database_url else None
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False) if engine else None


class UnavailableSession:
    def execute(self, *_args, **_kwargs):
        raise SQLAlchemyError("DATABASE_URL is not configured")


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        yield UnavailableSession()  # type: ignore[misc]
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
