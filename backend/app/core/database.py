from typing import Generator, Optional
from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()


def get_db(request: Request = None) -> Generator[Session, None, None]:
    """
    Tenant-aware database session dependency.
    If called within a FastAPI request, dynamically routes to the institution's database.
    If called without a request (e.g. scripts or background tasks), yields the central session.
    """
    if request is not None:
        try:
            from app.core.tenant_context import resolve_tenant_database_name, get_tenant_sessionmaker
            db_name = resolve_tenant_database_name(request)
            session_factory = get_tenant_sessionmaker(db_name)
            db = session_factory()
        except Exception:
            db = SessionLocal()
    else:
        db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

