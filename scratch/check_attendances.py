import sys, os
from pathlib import Path

BACKEND_DIR = Path("backend").resolve()
sys.path.insert(0, str(BACKEND_DIR))
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("--- Attendances by year ---")
    rows = conn.execute(text("""
        SELECT academic_year, count(*), count(distinct student_id), count(distinct class_id)
        FROM attendances
        GROUP BY academic_year
    """)).fetchall()
    for r in rows:
        print(r)
