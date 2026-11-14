import sys, os
from pathlib import Path

BACKEND_DIR = Path("backend").resolve()
sys.path.insert(0, str(BACKEND_DIR))
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("--- Students in Class 1 ---")
    rows = conn.execute(text("SELECT id, student_id, class_id, academic_year, status FROM student_enrollments WHERE class_id = 1")).mappings().all()
    for r in rows:
        # Check if student is already enrolled in 2026/2027
        enr26 = conn.execute(text(f"SELECT id, class_id, academic_year, status FROM student_enrollments WHERE student_id = {r['student_id']} AND academic_year = '2026/2027'")).mappings().first()
        print(f"Enrollment {r['id']}: student {r['student_id']} (class 1, yr={r['academic_year']}, st={r['status']}) -> Has 2026/2027 enr: {dict(enr26) if enr26 else None}")

    print("\n--- Students in Class 50 ---")
    rows = conn.execute(text("SELECT id, student_id, class_id, academic_year, status FROM student_enrollments WHERE class_id = 50")).mappings().all()
    for r in rows:
        enr26 = conn.execute(text(f"SELECT id, class_id, academic_year, status FROM student_enrollments WHERE student_id = {r['student_id']} AND academic_year = '2026/2027'")).mappings().first()
        print(f"Enrollment {r['id']}: student {r['student_id']} (class 50, yr={r['academic_year']}, st={r['status']}) -> Has 2026/2027 enr: {dict(enr26) if enr26 else None}")

    print("\n--- Students in Class 58 ---")
    rows = conn.execute(text("SELECT id, student_id, class_id, academic_year, status FROM student_enrollments WHERE class_id = 58")).mappings().all()
    for r in rows:
        enr26 = conn.execute(text(f"SELECT id, class_id, academic_year, status FROM student_enrollments WHERE student_id = {r['student_id']} AND academic_year = '2026/2027'")).mappings().first()
        print(f"Enrollment {r['id']}: student {r['student_id']} (class 58, yr={r['academic_year']}, st={r['status']}) -> Has 2026/2027 enr: {dict(enr26) if enr26 else None}")
