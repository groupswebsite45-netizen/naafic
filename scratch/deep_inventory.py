import sys, os
from pathlib import Path

BACKEND_DIR = Path("backend").resolve()
sys.path.insert(0, str(BACKEND_DIR))
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.database import engine
from sqlalchemy import text, inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

with engine.connect() as conn:
    print("=================== ACADEMIC YEAR INVENTORY ===================")
    for table in tables:
        cols = [c["name"] for c in inspector.get_columns(table)]
        year_cols = [c for c in cols if "year" in c.lower() or "academic" in c.lower()]
        for yc in year_cols:
            rows = conn.execute(text(f"""
                SELECT {yc}, count(*) 
                FROM {table} 
                WHERE {yc} != '2026/2027' OR {yc} IS NULL
                GROUP BY {yc}
            """)).fetchall()
            if rows:
                print(f"\n{table}.{yc} (non-2026/2027 rows):")
                for r in rows:
                    print(f"   value='{r[0]}' -> count={r[1]}")

print("\n=================== FOREIGN KEY & RELATIONSHIP CHECK ===================")
# Check classes: what classes exist in non-2026/2027?
with engine.connect() as conn:
    classes = conn.execute(text("""
        SELECT id, name, division, level, section, academic_year, status 
        FROM classes 
        WHERE academic_year != '2026/2027'
    """)).mappings().all()
    print(f"Non-2026/2027 classes count: {len(classes)}")
    for c in classes[:15]:
        print(f"   ID {c['id']}: '{c['name']}' (lvl={c['level']}, sec={c['section']}, div={c['division']}) year='{c['academic_year']}' status={c['status']}")
    
    # Check if these classes have enrollments, attendances, timetables, etc.
    class_ids = [c['id'] for c in classes]
    if class_ids:
        c_tuple = tuple(class_ids) if len(class_ids) > 1 else f"({class_ids[0]})"
        print(f"Enrollments in non-2026/2027 classes: {conn.execute(text(f'SELECT count(*) FROM student_enrollments WHERE class_id IN {c_tuple}')).scalar()}")
        print(f"Attendances in non-2026/2027 classes: {conn.execute(text(f'SELECT count(*) FROM attendances WHERE class_id IN {c_tuple}')).scalar()}")
        print(f"Timetables in non-2026/2027 classes: {conn.execute(text(f'SELECT count(*) FROM timetables WHERE class_id IN {c_tuple}')).scalar()}")
        print(f"Exams in non-2026/2027 classes: {conn.execute(text(f'SELECT count(*) FROM exams WHERE class_id IN {c_tuple}')).scalar()}")
        print(f"Teacher assignments in non-2026/2027 classes: {conn.execute(text(f'SELECT count(*) FROM teacher_assignments WHERE class_id IN {c_tuple}')).scalar()}")
