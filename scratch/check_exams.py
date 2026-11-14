import sys, os
from pathlib import Path

BACKEND_DIR = Path("backend").resolve()
sys.path.insert(0, str(BACKEND_DIR))
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("--- Exams by year ---")
    rows = conn.execute(text("""
        SELECT id, name, academic_year, class_id, subject_id, exam_type, status
        FROM exams
        WHERE academic_year != '2026/2027'
    """)).mappings().all()
    print("Total non-2026/2027 exams:", len(rows))
    for r in rows:
        print(dict(r))
