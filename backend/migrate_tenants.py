import logging
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.tenant_provisioner import get_tenant_db_url, get_server_db_url
from app.core.database import Base
import app.models  # load all models

logger = logging.getLogger("tenant_migrator")

def migrate_database(db_name: str) -> None:
    print(f"--> Migrating database: {db_name}")
    db_url = get_tenant_db_url(db_name)
    engine = create_engine(db_url, pool_pre_ping=True)
    is_postgres = "postgres" in db_url.lower()

    # 1. Create any missing tables defined in Base.metadata
    Base.metadata.create_all(bind=engine)

    # 2. Add any missing columns to timetables
    with engine.connect() as conn:
        cols_query = text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'timetables' AND table_schema = " + 
            ("current_schema()" if is_postgres else "DATABASE()")
        )
        existing_cols = {r[0].lower() for r in conn.execute(cols_query).fetchall()}

        if existing_cols:
            if "period_number" not in existing_cols:
                print(f"  Adding timetables.period_number to {db_name}")
                conn.execute(text("ALTER TABLE timetables ADD COLUMN period_number INTEGER;"))
                if is_postgres:
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_timetables_period_number ON timetables (period_number);"))

            if "is_break" not in existing_cols:
                print(f"  Adding timetables.is_break to {db_name}")
                if is_postgres:
                    conn.execute(text("ALTER TABLE timetables ADD COLUMN is_break BOOLEAN DEFAULT false NOT NULL;"))
                else:
                    conn.execute(text("ALTER TABLE timetables ADD COLUMN is_break BOOLEAN DEFAULT false NOT NULL;"))

            if "published_at" not in existing_cols:
                print(f"  Adding timetables.published_at to {db_name}")
                if is_postgres:
                    conn.execute(text("ALTER TABLE timetables ADD COLUMN published_at TIMESTAMP WITH TIME ZONE;"))
                else:
                    conn.execute(text("ALTER TABLE timetables ADD COLUMN published_at DATETIME;"))

            if "published_by_id" not in existing_cols:
                print(f"  Adding timetables.published_by_id to {db_name}")
                conn.execute(text("ALTER TABLE timetables ADD COLUMN published_by_id INTEGER;"))
                if is_postgres:
                    conn.execute(text(
                        "DO $$ BEGIN "
                        "  ALTER TABLE timetables ADD CONSTRAINT fk_timetables_published_by_id "
                        "  FOREIGN KEY (published_by_id) REFERENCES users(id) ON DELETE SET NULL; "
                        "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
                    ))

            # 3. Ensure default timetable_settings exists
            has_setting = conn.execute(text("SELECT count(*) FROM timetable_settings;")).scalar()
            if has_setting == 0:
                print(f"  Seeding default timetable_settings for {db_name}")
                conn.execute(text("""
                    INSERT INTO timetable_settings (academic_year, division, school_days, start_time, end_time, period_duration_minutes, break_duration_minutes, break_after_period, lunch_duration_minutes, lunch_after_period, periods_per_day, is_active, created_at, updated_at)
                    VALUES ('2026/2027', 'ALL', 'Saturday,Sunday,Monday,Tuesday,Wednesday,Thursday', '07:30:00', '13:30:00', 45, 20, 3, 30, 5, 6, true, NOW(), NOW());
                """))
                conn.execute(text("""
                    INSERT INTO timetable_settings (academic_year, division, school_days, start_time, end_time, period_duration_minutes, break_duration_minutes, break_after_period, lunch_duration_minutes, lunch_after_period, periods_per_day, is_active, created_at, updated_at)
                    VALUES ('2026-2027', 'ALL', 'Saturday,Sunday,Monday,Tuesday,Wednesday,Thursday', '07:30:00', '13:30:00', 45, 20, 3, 30, 5, 6, true, NOW(), NOW());
                """))

        conn.commit()
    engine.dispose()
    print(f"Migration completed for {db_name}")

def migrate_all_tenants():
    # 1. Migrate central DB
    central_db = settings.DATABASE_URL.rsplit("/", 1)[-1].split("?")[0] or "hawlwadaag_school_db"
    migrate_database(central_db)

    # 2. Migrate registered tenant databases
    central_engine = create_engine(get_tenant_db_url(central_db), pool_pre_ping=True)
    with central_engine.connect() as conn:
        try:
            rows = conn.execute(text("SELECT database_name FROM institutions WHERE database_name IS NOT NULL;")).fetchall()
            tenant_dbs = {r[0].strip() for r in rows if r[0] and r[0].strip() != central_db}
        except Exception as exc:
            print(f"Could not read institutions: {exc}")
            tenant_dbs = set()
    central_engine.dispose()

    for db_name in tenant_dbs:
        try:
            migrate_database(db_name)
        except Exception as exc:
            print(f"Failed migrating {db_name}: {exc}")

if __name__ == "__main__":
    migrate_all_tenants()
