import sys
from pathlib import Path

BACKEND_DIR = Path("backend").resolve()
sys.path.insert(0, str(BACKEND_DIR))
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.database import engine
from sqlalchemy import text, inspect

with engine.begin() as conn:
    # 1. Classes with academic_year != '2026/2027'
    classes = conn.execute(text("SELECT id, name, division, level, section, academic_year FROM classes WHERE academic_year != '2026/2027'")).fetchall()
    print(f"Non-2026/2027 classes: {len(classes)}")
    for c in classes:
        # Check if identical class exists in 2026/2027
        existing = conn.execute(text("""
            SELECT id FROM classes 
            WHERE academic_year = '2026/2027' 
              AND division = :div 
              AND level = :lvl 
              AND section = :sec
        """), {"div": c.division, "lvl": c.level, "sec": c.section}).fetchone()

        if existing:
            target_id = existing.id
            print(f"  Class {c.id} ({c.name}) has duplicate {target_id} in 2026/2027. Remapping references and deleting.")
            # Move enrollments or delete if student already enrolled in 2026/2027
            for enr in conn.execute(text("SELECT id, student_id FROM student_enrollments WHERE class_id = :cid"), {"cid": c.id}).fetchall():
                already = conn.execute(text("SELECT id FROM student_enrollments WHERE student_id = :sid AND academic_year = '2026/2027'"), {"sid": enr.student_id}).fetchone()
                if already:
                    conn.execute(text("DELETE FROM student_enrollments WHERE id = :eid"), {"eid": enr.id})
                else:
                    conn.execute(text("UPDATE student_enrollments SET class_id = :tid, academic_year = '2026/2027' WHERE id = :eid"), {"tid": target_id, "eid": enr.id})
            
            # Reassign timetable, attendance, exams
            conn.execute(text("DELETE FROM timetables WHERE class_id = :cid"), {"cid": c.id})
            conn.execute(text("DELETE FROM teacher_assignments WHERE class_id = :cid"), {"cid": c.id})
            conn.execute(text("DELETE FROM attendances WHERE class_id = :cid"), {"cid": c.id})
            conn.execute(text("DELETE FROM classes WHERE id = :cid"), {"cid": c.id})
        else:
            conn.execute(text("UPDATE classes SET academic_year = '2026/2027' WHERE id = :cid"), {"cid": c.id})

    # 2. Student enrollments - delete any duplicate enrollment for students who already have a 2026/2027 enrollment
    conn.execute(text("""
        DELETE FROM student_enrollments
        WHERE academic_year != '2026/2027'
          AND student_id IN (
              SELECT student_id FROM student_enrollments WHERE academic_year = '2026/2027'
          )
    """))
    conn.execute(text("UPDATE student_enrollments SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    
    # 3. Attendances
    conn.execute(text("UPDATE attendances SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE attendance_submissions SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))

    # 4. Teacher assignments
    # Delete any duplicate assignments before updating
    conn.execute(text("""
        DELETE FROM teacher_assignments ta1
        USING teacher_assignments ta2
        WHERE ta1.id > ta2.id
          AND ta1.class_id = ta2.class_id
          AND ta1.subject_id = ta2.subject_id
          AND (ta1.academic_year != '2026/2027' OR ta2.academic_year = '2026/2027')
    """))
    conn.execute(text("UPDATE teacher_assignments SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))

    # 5. Timetables
    conn.execute(text("""
        DELETE FROM timetables t1
        USING timetables t2
        WHERE t1.id > t2.id
          AND t1.class_id = t2.class_id
          AND t1.day_of_week = t2.day_of_week
          AND t1.period_number = t2.period_number
    """))
    conn.execute(text("UPDATE timetables SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))

    # 6. Notifications & Result submissions & views
    conn.execute(text("UPDATE notifications SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE student_result_views SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE result_submissions SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    
    # 7. Teacher availabilities
    conn.execute(text("UPDATE teacher_availabilities SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))

    # 8. Class promotions
    conn.execute(text("UPDATE class_promotion_batches SET target_academic_year = '2026/2027' WHERE target_academic_year != '2026/2027'"))
    conn.execute(text("UPDATE class_promotion_batches SET source_academic_year = '2026/2027' WHERE source_academic_year != '2026/2027'"))
    conn.execute(text("UPDATE class_promotion_records SET target_academic_year = '2026/2027' WHERE target_academic_year != '2026/2027'"))
    conn.execute(text("UPDATE class_promotion_records SET source_academic_year = '2026/2027' WHERE source_academic_year != '2026/2027'"))

print("All tables successfully normalized.")
