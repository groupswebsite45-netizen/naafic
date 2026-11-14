import sys, os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print('Total students:', conn.execute(text('SELECT count(*) FROM students')).scalar())
    print('Students with enrollment:', conn.execute(text('SELECT count(distinct student_id) FROM student_enrollments')).scalar())
    print('Students enrolled in 2026/2027:', conn.execute(text("SELECT count(distinct student_id) FROM student_enrollments WHERE academic_year = '2026/2027'")).scalar())
    print('Students enrolled in 2026-2027:', conn.execute(text("SELECT count(distinct student_id) FROM student_enrollments WHERE academic_year = '2026-2027'")).scalar())
    print('Students enrolled ONLY in other years (not 2026/2027):')
    rows = conn.execute(text("""
        SELECT se.academic_year, count(distinct se.student_id)
        FROM student_enrollments se
        WHERE se.student_id NOT IN (SELECT student_id FROM student_enrollments WHERE academic_year = '2026/2027')
        GROUP BY se.academic_year
    """)).fetchall()
    for r in rows:
        print(' ', r)
