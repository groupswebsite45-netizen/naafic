import sys, os
from pathlib import Path

BACKEND_DIR = Path("backend").resolve()
sys.path.insert(0, str(BACKEND_DIR))
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT e1.id as hyp_id, e1.student_id, e1.class_id as hyp_class, 
               e2.id as slash_id, e2.class_id as slash_class
        FROM student_enrollments e1
        LEFT JOIN student_enrollments e2 ON e1.student_id = e2.student_id AND e2.academic_year = '2026/2027'
        WHERE e1.academic_year = '2026-2027'
    """)).mappings().all()
    print("Total '2026-2027' enrollments:", len(rows))
    conflicts = [r for r in rows if r['slash_id'] is not None]
    no_conflicts = [r for r in rows if r['slash_id'] is None]
    print(f"Conflicts (already has '2026/2027'): {len(conflicts)}")
    for r in conflicts:
        print(f"  Student {r['student_id']}: hyphen_enr={r['hyp_id']} (class {r['hyp_class']}), slash_enr={r['slash_id']} (class {r['slash_class']})")
    print(f"No conflicts (only had '2026-2027'): {len(no_conflicts)}")
