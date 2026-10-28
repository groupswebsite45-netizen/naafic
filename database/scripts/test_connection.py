"""
Database connection test utility.
Checks if the local PostgreSQL server is reachable and verifies table structures.
Usage:
    python database/scripts/test_connection.py
"""
import sys
import os

# Add backend directory to sys.path to read settings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

try:
    from app.core.config import settings
    from sqlalchemy import create_engine, text

    print(f"Testing database connection to: {settings.DATABASE_URL.split('@')[-1]}")
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database(), version();"))
        db_name, version = result.fetchone()
        print(f"Successfully connected to PostgreSQL database: '{db_name}'")
        print(f"Database engine: {version.split(',')[0]}")

        # Check existing tables
        tables_res = conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
        ))
        tables = [row[0] for row in tables_res.fetchall()]
        print(f"Current tables in public schema ({len(tables)}): {', '.join(tables) if tables else 'None yet (Run migrations)'}")

except Exception as e:
    print(f"DATABASE CONNECTION ERROR: {e}")
    sys.exit(1)
