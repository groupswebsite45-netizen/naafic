import logging
from typing import Dict, Generator, Optional
from fastapi import Request
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from jose import jwt, JWTError

from app.core.config import settings
from app.core.tenant_provisioner import get_tenant_db_url

logger = logging.getLogger(__name__)

# Central database engine & sessionmaker (points to 'sms' database)
_central_engine: Optional[Engine] = None
_central_sessionmaker: Optional[sessionmaker] = None

# Tenant database engines & sessionmakers cache
_tenant_engines: Dict[str, Engine] = {}
_tenant_sessionmakers: Dict[str, sessionmaker] = {}
_migrated_databases = set()


def _ensure_tenant_schema(engine: Engine, db_name: str) -> None:
    if db_name in _migrated_databases:
        return
    _migrated_databases.add(db_name)
    try:
        from app.core.database import Base
        from app.models.timetable_setting import TimetableSetting
        from app.models.teacher_availability import TeacherAvailability
        Base.metadata.create_all(bind=engine, tables=[
            TimetableSetting.__table__,
            TeacherAvailability.__table__
        ])
        with engine.connect() as conn:
            cols = {
                r[0].lower() for r in conn.execute(text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'timetables'"
                )).fetchall()
            }
            if cols and "period_number" not in cols:
                conn.execute(text("ALTER TABLE timetables ADD COLUMN IF NOT EXISTS period_number INTEGER;"))
                conn.execute(text("ALTER TABLE timetables ADD COLUMN IF NOT EXISTS is_break BOOLEAN DEFAULT false NOT NULL;"))
                conn.execute(text("ALTER TABLE timetables ADD COLUMN IF NOT EXISTS published_at TIMESTAMP WITH TIME ZONE;"))
                conn.execute(text("ALTER TABLE timetables ADD COLUMN IF NOT EXISTS published_by_id INTEGER;"))
                conn.commit()

            student_cols = {
                r[0].lower() for r in conn.execute(text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'students'"
                )).fetchall()
            }
            if student_cols and "photo_path" not in student_cols:
                conn.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS photo_path VARCHAR(500);"))
                conn.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS photo_filename VARCHAR(255);"))
                conn.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS photo_mime_type VARCHAR(100);"))
                conn.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS photo_size INTEGER;"))
                conn.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS photo_uploaded_at TIMESTAMP WITH TIME ZONE;"))
                conn.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS photo_updated_at TIMESTAMP WITH TIME ZONE;"))
                conn.commit()

            exam_cols = {
                r[0].lower() for r in conn.execute(text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'exams'"
                )).fetchall()
            }
            if exam_cols and "published_at" not in exam_cols:
                conn.execute(text("ALTER TABLE exams ADD COLUMN IF NOT EXISTS published_at TIMESTAMP WITH TIME ZONE;"))
                conn.execute(text("ALTER TABLE exams ADD COLUMN IF NOT EXISTS published_by_id INTEGER;"))
                conn.commit()
    except Exception as exc:
        logger.debug(f"Schema auto-check on {db_name}: {exc}")


def get_central_engine() -> Engine:
    global _central_engine
    if _central_engine is None:
        _central_engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=False,
        )
    return _central_engine


def get_central_sessionmaker() -> sessionmaker:
    global _central_sessionmaker
    if _central_sessionmaker is None:
        _central_sessionmaker = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_central_engine(),
            expire_on_commit=False,
        )
    return _central_sessionmaker


def get_central_db() -> Generator[Session, None, None]:
    """Dependency that yields a session directly to the central Super Admin database."""
    session = get_central_sessionmaker()()
    try:
        yield session
    finally:
        session.close()


def get_tenant_engine(database_name: str) -> Engine:
    """Returns or creates a cached SQLAlchemy Engine for the specified tenant database."""
    clean_db = (database_name or "").strip().lower()
    default_db = get_default_database_name().lower()
    if not clean_db or clean_db in ["sms", "hawlwadaag_school_db", default_db]:
        return get_central_engine()

    if clean_db not in _tenant_engines:
        url = get_tenant_db_url(clean_db)
        eng = create_engine(
            url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=False,
        )
        _ensure_tenant_schema(eng, clean_db)
        _tenant_engines[clean_db] = eng
    return _tenant_engines[clean_db]


def get_tenant_sessionmaker(database_name: str) -> sessionmaker:
    """Returns or creates a cached sessionmaker for the specified tenant database."""
    clean_db = (database_name or "").strip().lower()
    default_db = get_default_database_name().lower()
    if not clean_db or clean_db in ["sms", default_db]:
        return get_central_sessionmaker()

    if clean_db not in _tenant_sessionmakers:
        engine = get_tenant_engine(clean_db)
        _tenant_sessionmakers[clean_db] = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            expire_on_commit=False,
        )
    return _tenant_sessionmakers[clean_db]


def extract_tenant_context_from_request(request: Request) -> Dict[str, Optional[str]]:
    """
    Extracts institution identifiers with strict isolation:
    1. JWT Authorization Bearer token payload is the authoritative source for authenticated requests.
       Tenant users CANNOT override their tenant context via request headers or query params.
    2. Super Admins may target a specific tenant database via X-Institution-Id / X-Institution-Code.
    3. Unauthenticated requests (e.g. public settings, tenant login branding) read headers / query params.
    """
    context: Dict[str, Optional[str]] = {
        "code": None,
        "id": None,
        "db_name": None,
        "is_super_admin": False,
    }

    # 1. Inspect JWT Token first if present
    token = None
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
    elif request.query_params.get("token"):
        token = request.query_params.get("token").strip()

    if token:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            is_super = bool(payload.get("is_superuser")) or any(
                str(r).upper() in ["SUPER_ADMIN", "SUPERADMIN"] for r in (payload.get("roles") or [])
            )
            context["is_super_admin"] = is_super

            if not is_super:
                # For tenant users, token claims are IMMUTABLE & AUTHORITATIVE
                if payload.get("database_name"):
                    context["db_name"] = str(payload.get("database_name"))
                if payload.get("institution_code"):
                    context["code"] = str(payload.get("institution_code"))
                if payload.get("institution_id"):
                    context["id"] = str(payload.get("institution_id"))
                return context
        except JWTError:
            pass

    # 2. For Super Admin or unauthenticated requests, inspect request headers and query parameters
    header_code = request.headers.get("x-institution-code", "").strip() or None
    header_id = request.headers.get("x-institution-id", "").strip() or None
    query_code = (
        request.query_params.get("institution_code")
        or request.query_params.get("institution")
        or None
    )
    query_id = request.query_params.get("institution_id") or None

    context["code"] = header_code or query_code
    context["id"] = header_id or query_id

    return context


def get_default_database_name() -> str:
    url = settings.DATABASE_URL
    if "/" in url:
        db_part = url.rsplit("/", 1)[-1].split("?")[0]
        if db_part:
            return db_part
    return "sms"


def resolve_tenant_database_name(request: Request) -> str:
    """
    Determines the appropriate database name for the current request.
    - If route is /api/v1/super-admin/* -> returns central database.
    - If institution context is specified -> queries central institutions table to find assigned database_name.
    - Fallback -> returns configured default database (preserving existing Hawlwadaag School data).
    """
    default_db = get_default_database_name()

    # 1. Super Admin operations always use the central database
    path = request.url.path
    if "/api/v1/super-admin" in path:
        return default_db

    ctx = extract_tenant_context_from_request(request)

    # If database_name is already verified from a trusted JWT token
    if ctx.get("db_name"):
        return ctx["db_name"]

    # If code or id is provided, look up in central database
    if ctx.get("code") or ctx.get("id"):
        central_session = get_central_sessionmaker()()
        try:
            query = text(
                "SELECT id, code, database_name FROM institutions WHERE "
                + ("code = :code" if ctx.get("code") else "id = :id")
                + " LIMIT 1;"
            )
            params = {"code": ctx["code"]} if ctx.get("code") else {"id": int(ctx["id"])}
            row = central_session.execute(query, params).fetchone()

            if row and row[2]:
                target_db = row[2].strip()
                return target_db
        except Exception as e:
            logger.warning(f"Error resolving tenant database from central institutions: {e}")
        finally:
            central_session.close()

    # Default fallback: central database (Hawlwadaag School)
    return default_db


def get_db(request: Request) -> Generator[Session, None, None]:
    """
    Tenant-aware database session dependency.
    Automatically routes requests to the institution's dedicated database.
    """
    db_name = resolve_tenant_database_name(request)
    session_factory = get_tenant_sessionmaker(db_name)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
