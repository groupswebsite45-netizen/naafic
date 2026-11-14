import sys, os
from pathlib import Path

BACKEND_DIR = Path("backend").resolve()
sys.path.insert(0, str(BACKEND_DIR))
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.database import engine
from sqlalchemy import text, inspect

def run_migration(dry_run=True):
    with engine.begin() as conn:
        print(f"--- Starting Migration (dry_run={dry_run}) ---")
        
        # 1. Update simple tables without unique conflict risks
        conn.execute(text("UPDATE notifications SET academic_year = '2026/2027' WHERE academic_year != '2026/2027' OR academic_year IS NULL"))
        conn.execute(text("UPDATE student_result_views SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
        conn.execute(text("UPDATE fee_structures SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
        conn.execute(text("UPDATE student_fees SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
        conn.execute(text("UPDATE teacher_availabilities SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
        conn.execute(text("UPDATE student_import_logs SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
        conn.execute(text("UPDATE class_promotion_batches SET source_academic_year = '2026/2027', target_academic_year = '2026/2027' WHERE source_academic_year != '2026/2027' OR target_academic_year != '2026/2027'"))
        conn.execute(text("UPDATE class_promotion_records SET source_academic_year = '2026/2027', target_academic_year = '2026/2027' WHERE source_academic_year != '2026/2027' OR target_academic_year != '2026/2027'"))
        conn.execute(text("UPDATE result_release_batches SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
        conn.execute(text("UPDATE result_submissions SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
        conn.execute(text("UPDATE attendance_submissions SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
        conn.execute(text("UPDATE teacher_attendances SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
        conn.execute(text("UPDATE timetable_settings SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))

        # 2. System settings: ensure academic_year_current is 2026/2027
        conn.execute(text("UPDATE system_settings SET value = '2026/2027' WHERE key = 'academic_year_current'"))

        # 3. Handle Timetables
        # Class 50 -> Class 29
        conn.execute(text("UPDATE timetables SET class_id = 29 WHERE class_id = 50"))
        conn.execute(text("UPDATE timetables SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))

        # 4. Handle Exams
        # Class 1 -> Class 29
        conn.execute(text("UPDATE exams SET class_id = 29 WHERE class_id = 1"))
        conn.execute(text("UPDATE exams SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))

        # 5. Handle Attendances
        # Class 1 -> Class 29
        conn.execute(text("UPDATE attendances SET class_id = 29 WHERE class_id = 1"))
        conn.execute(text("UPDATE attendances SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))

        # 6. Handle Teacher Assignments
        # Delete duplicate test assignments (id 51, 56, 61) before mapping class 1 -> 29
        conn.execute(text("DELETE FROM teacher_assignments WHERE id IN (51, 56, 61)"))
        conn.execute(text("UPDATE teacher_assignments SET class_id = 29 WHERE class_id = 1"))
        conn.execute(text("UPDATE teacher_assignments SET class_id = 94 WHERE class_id = 93"))
        conn.execute(text("UPDATE teacher_assignments SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))

        # 7. Handle Student Enrollments
        # Reassign class 50 -> class 29, class 58 -> class 37
        conn.execute(text("UPDATE student_enrollments SET class_id = 29 WHERE class_id = 50"))
        conn.execute(text("UPDATE student_enrollments SET class_id = 37 WHERE class_id = 58"))
        conn.execute(text("UPDATE student_enrollments SET class_id = 29 WHERE class_id = 1 AND student_id NOT IN (1, 2, 3, 4, 5, 6, 7, 8)"))

        # Delete duplicate enrollments
        dup_enrs = [1, 2, 3, 4, 5, 6, 7, 8, 111, 90, 145, 146, 147, 148, 174, 225]
        conn.execute(text(f"DELETE FROM student_enrollments WHERE id IN ({','.join(map(str, dup_enrs))})"))

        # Now update all remaining student_enrollments to 2026/2027
        conn.execute(text("UPDATE student_enrollments SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))

        # 8. Handle Classes
        # Classes 3, 4, 5, 6, 7, 19, 22 don't collide
        conn.execute(text("UPDATE classes SET academic_year = '2026/2027' WHERE id IN (3, 4, 5, 6, 7, 19, 22)"))
        # The other old classes (1, 2, 8, 93, 50-73) are now unreferenced, let's delete them
        conn.execute(text("DELETE FROM classes WHERE id IN (1, 2, 8, 93) OR (id >= 50 AND id <= 73)"))

        # Now check if ANY non-2026/2027 records remain in the entire database!
        inspector = inspect(conn)
        tables = inspector.get_table_names()
        any_remaining = 0
        for table in tables:
            cols = [c["name"] for c in inspector.get_columns(table)]
            year_cols = [c for c in cols if "year" in c.lower() or "academic" in c.lower()]
            for yc in year_cols:
                cnt = conn.execute(text(f"SELECT count(*) FROM {table} WHERE {yc} != '2026/2027'")).scalar()
                if cnt > 0:
                    print(f"REMAINING: {table}.{yc} has {cnt} non-2026/2027 rows!")
                    any_remaining += cnt

        if any_remaining == 0:
            print("SUCCESS! Zero non-2026/2027 rows in the entire database!")
        else:
            print(f"FAILED: {any_remaining} non-2026/2027 rows remain!")

        if dry_run:
            print("Rolling back dry run transaction...")
            raise Exception("DRY RUN ROLLBACK")
        else:
            print("Committed changes!")

if __name__ == "__main__":
    try:
        run_migration(dry_run=True)
    except Exception as e:
        if str(e) == "DRY RUN ROLLBACK":
            print("Dry run completed cleanly without database errors!")
        else:
            raise
