import sys, os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(BACKEND_DIR))
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.database import engine
from sqlalchemy import text

# Run the migration for real
from scratch.migrate_academic_years_db import run_migration
run_migration(dry_run=False)

with engine.connect() as conn:
    print("\n--- POST-MIGRATION STATS ---")
    print("Total students:", conn.execute(text("SELECT count(*) FROM students")).scalar())
    print("Distinct enrolled students:", conn.execute(text("SELECT count(distinct student_id) FROM student_enrollments")).scalar())
    print("Active 2026/2027 enrollments:", conn.execute(text("SELECT count(*) FROM student_enrollments WHERE academic_year = '2026/2027' AND status = 'ACTIVE'")).scalar())
    print("Total classes:", conn.execute(text("SELECT count(*) FROM classes")).scalar())
    print("All classes year:", conn.execute(text("SELECT DISTINCT academic_year FROM classes")).fetchall())
    print("Total exams:", conn.execute(text("SELECT count(*) FROM exams")).scalar())
    print("All exams year:", conn.execute(text("SELECT DISTINCT academic_year FROM exams")).fetchall())
    print("Total attendances:", conn.execute(text("SELECT count(*) FROM attendances")).scalar())
    print("All attendances year:", conn.execute(text("SELECT DISTINCT academic_year FROM attendances")).fetchall())
    print("Total teacher assignments:", conn.execute(text("SELECT count(*) FROM teacher_assignments")).scalar())
    print("All teacher assignments year:", conn.execute(text("SELECT DISTINCT academic_year FROM teacher_assignments")).fetchall())
    print("Total fee structures:", conn.execute(text("SELECT count(*) FROM fee_structures")).scalar())
    print("All fee structures year:", conn.execute(text("SELECT DISTINCT academic_year FROM fee_structures")).fetchall())
    print("Total student fees:", conn.execute(text("SELECT count(*) FROM student_fees")).scalar())
    print("All student fees year:", conn.execute(text("SELECT DISTINCT academic_year FROM student_fees")).fetchall())
    print("Current academic year setting:", conn.execute(text("SELECT value FROM system_settings WHERE key = 'academic_year_current'")).scalar())
