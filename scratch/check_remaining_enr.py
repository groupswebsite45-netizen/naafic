import sys, os
from pathlib import Path

BACKEND_DIR = Path("backend").resolve()
sys.path.insert(0, str(BACKEND_DIR))
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("--- 2025-2026 enrollments (2 rows) ---")
    rows = conn.execute(text("SELECT * FROM student_enrollments WHERE academic_year = '2025-2026'")).mappings().all()
    for r in rows:
        print(dict(r))

    print("\n--- 2027/2028 enrollments (9 rows) ---")
    rows = conn.execute(text("SELECT * FROM student_enrollments WHERE academic_year = '2027/2028'")).mappings().all()
    for r in rows:
        print(dict(r))
