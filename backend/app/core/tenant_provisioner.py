import re
import unicodedata
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.security import get_password_hash
from app.core.database import Base


def get_server_db_url() -> str:
    """
    Returns database connection URL without a specific database selected,
    used for administrative tasks such as CREATE DATABASE.
    """
    url = settings.DATABASE_URL
    if "mysql" in url:
        match = re.match(r"(mysql\+pymysql://[^/]+)(/?[^?]*)(.*)", url)
        if match:
            base_url = match.group(1)
            query_part = match.group(3) or ""
            return f"{base_url}/{query_part}"
    elif "postgresql" in url:
        match = re.match(r"((?:postgresql|postgresql\+psycopg2)://[^/]+)(/?[^?]*)(.*)", url)
        if match:
            base_url = match.group(1)
            query_part = match.group(3) or ""
            return f"{base_url}/postgres{query_part}"
    return url


def get_tenant_db_url(database_name: str) -> str:
    """
    Constructs the SQLAlchemy connection URL for a specific tenant database.
    """
    url = settings.DATABASE_URL
    if "mysql" in url:
        match = re.match(r"(mysql\+pymysql://[^/]+)(/?[^?]*)(.*)", url)
        if match:
            base_url = match.group(1)
            query_part = match.group(3) or "?charset=utf8mb4"
            return f"{base_url}/{database_name}{query_part}"
    elif "postgresql" in url:
        match = re.match(r"((?:postgresql|postgresql\+psycopg2)://[^/]+)(/?[^?]*)(.*)", url)
        if match:
            base_url = match.group(1)
            query_part = match.group(3) or ""
            return f"{base_url}/{database_name}{query_part}"
    return url


def normalize_slug(text_val: str) -> str:
    """
    Normalizes a text string into a clean lowercase identifier.
    e.g. 'Waberi Secondary School' -> 'waberi_secondary_school'
    """
    # Normalize unicode characters
    val = unicodedata.normalize("NFKD", text_val)
    val = val.encode("ascii", "ignore").decode("ascii")
    val = val.lower()
    # Replace any non-alphanumeric character with underscore
    val = re.sub(r"[^a-z0-9]+", "_", val)
    # Strip leading/trailing underscores
    val = val.strip("_")
    # Collapse multiple consecutive underscores
    val = re.sub(r"_+", "_", val)
    return val


def generate_tenant_database_name(institution_name: str, code: Optional[str] = None) -> str:
    """
    Generates a unique, valid MySQL database name derived from the institution's name.
    Prefix: 'somroyal_'
    MySQL identifier limit: 64 characters.
    Example: 'somroyal_waberi_secondary_school'
    """
    slug = normalize_slug(institution_name)
    if not slug:
        slug = normalize_slug(code or "institution") or "institution"

    prefix = "somroyal_"
    # Limit slug length to 50 chars so prefix (9) + slug (50) + suffix buffer (5) <= 64 chars
    slug = slug[:50].rstrip("_")
    base_name = f"{prefix}{slug}"

    # Verify uniqueness in PostgreSQL or MySQL
    server_url = get_server_db_url()
    server_engine = create_engine(server_url, pool_pre_ping=True)

    with server_engine.connect() as conn:
        if "postgres" in server_url.lower():
            res = conn.execute(text("SELECT datname FROM pg_database;"))
        else:
            res = conn.execute(text("SHOW DATABASES;"))
        existing_dbs = {row[0].lower() for row in res.fetchall()}

    db_name = base_name
    counter = 2
    while db_name.lower() in existing_dbs:
        suffix = f"_{counter}"
        allowed_slug_len = 64 - len(prefix) - len(suffix)
        db_name = f"{prefix}{slug[:allowed_slug_len].rstrip('_')}{suffix}"
        counter += 1

    server_engine.dispose()
    return db_name


def create_tenant_database(database_name: str) -> bool:
    """
    Executes CREATE DATABASE IF NOT EXISTS on PostgreSQL or MySQL server.
    """
    server_url = get_server_db_url()
    safe_db_name = re.sub(r"[^a-zA-Z0-9_]", "", database_name)

    if "postgres" in server_url.lower():
        # In PostgreSQL, CREATE DATABASE cannot run inside a transaction block.
        # It must use isolation_level="AUTOCOMMIT"
        pg_engine = create_engine(server_url, isolation_level="AUTOCOMMIT", pool_pre_ping=True)
        with pg_engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dname"),
                {"dname": safe_db_name}
            ).scalar()
            if not exists:
                conn.execute(text(f'CREATE DATABASE "{safe_db_name}";'))
        pg_engine.dispose()
        return True
    else:
        server_engine = create_engine(server_url, pool_pre_ping=True)
        with server_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{safe_db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
            conn.commit()
        server_engine.dispose()
        return True


def provision_tenant_schema_and_admin(
    database_name: str,
    admin_data: Dict[str, Any],
    institution_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Initializes a newly created tenant database:
    1. Creates all SMS tables (empty of students, teachers, classes, exams, fees, etc.).
    2. Seeds default roles (ADMIN, TEACHER, STUDENT, STAFF).
    3. Seeds initial institution system settings.
    4. Creates the institution's initial administrator account.
    """
    from app.models import Role, User, UserRole, SystemSetting

    tenant_url = get_tenant_db_url(database_name)
    tenant_engine = create_engine(tenant_url, pool_pre_ping=True)

    # 1. Create schema tables using SQLAlchemy metadata
    Base.metadata.create_all(bind=tenant_engine)

    # 2. Seed default roles and initial admin
    TenantSession = sessionmaker(bind=tenant_engine, autocommit=False, autoflush=False)
    db: Session = TenantSession()

    admin_user_id = None
    try:
        # Default system roles
        default_roles = [
            ("ADMIN", "Full Administrator with complete access to institution SMS"),
            ("TEACHER", "Teacher with access to classes, attendance, and exam grading"),
            ("STUDENT", "Student with access to grades, attendance, and timetable"),
            ("STAFF", "Institutional Staff member"),
            ("PARENT", "Parent/Guardian portal access")
        ]

        roles_map = {}
        for role_name, desc in default_roles:
            r = db.query(Role).filter(Role.name == role_name).first()
            if not r:
                r = Role(name=role_name, description=desc, is_system=True)
                db.add(r)
                db.flush()
            roles_map[role_name] = r

        # Seed essential system settings
        default_settings = {
            "school_name": institution_info.get("name", "Educational Institution"),
            "school_code": institution_info.get("code", "EMS-001"),
            "school_type": institution_info.get("type", "School"),
            "contact_email": institution_info.get("email", ""),
            "contact_phone": institution_info.get("phone", ""),
            "city": institution_info.get("city", "Mogadishu"),
            "currency": "USD",
            "active_academic_year": "2026-2027",
            "timezone": "Africa/Mogadishu",
        }

        for s_key, s_val in default_settings.items():
            if not db.query(SystemSetting).filter(SystemSetting.key == s_key).first():
                db.add(SystemSetting(key=s_key, value=str(s_val), description=f"Initial setting for {s_key}"))

        # Seed default timetable settings
        from app.models.timetable_setting import TimetableSetting
        from datetime import time
        if not db.query(TimetableSetting).first():
            db.add(TimetableSetting(
                academic_year="2026/2027",
                division="ALL",
                school_days="Saturday,Sunday,Monday,Tuesday,Wednesday,Thursday",
                start_time=time(7, 30),
                end_time=time(13, 30),
                period_duration_minutes=45,
                break_duration_minutes=20,
                break_after_period=3,
                lunch_duration_minutes=30,
                lunch_after_period=5,
                periods_per_day=6,
                is_active=True
            ))

        # Create the initial institution administrator
        admin_email = admin_data.get("email", "").strip()
        admin_username = admin_data.get("username", "").strip()
        admin_password = admin_data.get("password", "")
        admin_full_name = admin_data.get("full_name", "Institution Administrator").strip()
        admin_phone = admin_data.get("phone_number", "")

        existing_user = db.query(User).filter(
            (User.email == admin_email) | (User.username == admin_username)
        ).first()

        if not existing_user:
            admin_user = User(
                email=admin_email,
                username=admin_username,
                full_name=admin_full_name,
                phone_number=admin_phone,
                hashed_password=get_password_hash(admin_password),
                is_active=True,
                is_superuser=False,
            )
            db.add(admin_user)
            db.flush()

            # Assign ADMIN role
            if "ADMIN" in roles_map:
                ur = UserRole(user_id=admin_user.id, role_id=roles_map["ADMIN"].id)
                db.add(ur)

            db.commit()
            admin_user_id = admin_user.id
        else:
            admin_user_id = existing_user.id

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
        tenant_engine.dispose()

    return {
        "database_name": database_name,
        "admin_user_id": admin_user_id,
        "admin_username": admin_username,
        "admin_email": admin_email
    }


def delete_tenant_database(database_name: str) -> bool:
    """
    Drops the specified tenant database.
    Safety constraint: NEVER drops the central database.
    """
    protected = ["sms", "hawlwadaag_school_db", "postgres", "mysql", "information_schema", "performance_schema", "phpmyadmin"]
    if database_name.lower() in protected:
        raise ValueError(f"Refusing to drop protected database '{database_name}'.")

    server_url = get_server_db_url()
    safe_db_name = re.sub(r"[^a-zA-Z0-9_]", "", database_name)

    if "postgres" in server_url.lower():
        pg_engine = create_engine(server_url, isolation_level="AUTOCOMMIT", pool_pre_ping=True)
        with pg_engine.connect() as conn:
            conn.execute(text(f'DROP DATABASE IF EXISTS "{safe_db_name}";'))
        pg_engine.dispose()
        return True
    else:
        server_engine = create_engine(server_url, pool_pre_ping=True)
        with server_engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE IF EXISTS `{safe_db_name}`;"))
            conn.commit()
        server_engine.dispose()
        return True
