import os
import sys
from sqlalchemy import text
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine
from app.models.school_class import SchoolClass
from app.models.student_enrollment import StudentEnrollment
from app.models.teacher_assignment import TeacherAssignment
from app.models.timetable import Timetable
from app.models.exam import Exam, ExamResult
from app.models.attendance import Attendance
from app.models.fee import FeeStructure, StudentFee, FeePayment


def clean_and_consolidate_classes():
    db = SessionLocal()
    try:
        print(">>> 1. Pruning duplicate and test enrollments in test/generated classes (175, 177, 178, 179, 173)...")
        for tid in [175, 177, 178, 179, 173]:
            tc = db.query(SchoolClass).filter(SchoolClass.id == tid).first()
            if tc:
                del_cnt = db.query(StudentEnrollment).filter(StudentEnrollment.class_id == tid).delete()
                tc.status = "INACTIVE"
                db.commit()
                print(f"  Pruned {del_cnt} enrollments from test class ID {tid} ({tc.name}) and marked INACTIVE.")

        print(">>> 2. Removing empty duplicate classes (146, 176, 180)...")
        for empty_id in [146, 176, 180]:
            emp = db.query(SchoolClass).filter(SchoolClass.id == empty_id).first()
            if emp:
                en_cnt = db.query(StudentEnrollment).filter(StudentEnrollment.class_id == empty_id).count()
                ta_cnt = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == empty_id).count()
                ex_cnt = db.query(Exam).filter(Exam.class_id == empty_id).count()
                fs_cnt = db.query(FeeStructure).filter(FeeStructure.class_id == empty_id).count()
                sf_cnt = db.query(StudentFee).filter(StudentFee.class_id == empty_id).count()
                if en_cnt == 0 and ta_cnt == 0 and ex_cnt == 0 and fs_cnt == 0 and sf_cnt == 0:
                    db.delete(emp)
                    db.commit()
                    print(f"  Safely removed empty duplicate class ID {empty_id} ({emp.name}).")
                else:
                    emp.code = f"OLD-{emp.code}-{empty_id}"
                    emp.status = "INACTIVE"
                    db.commit()
                    print(f"  Class ID {empty_id} has dependents, renamed code and marked INACTIVE.")

        print(">>> 3. Normalizing Academic Year formatting to 'YYYY/YYYY' across tables...")
        with engine.begin() as conn:
            conn.execute(text("UPDATE classes SET academic_year = REPLACE(academic_year, '-', '/') WHERE academic_year LIKE '%-%';"))
            conn.execute(text("UPDATE student_enrollments SET academic_year = REPLACE(academic_year, '-', '/') WHERE academic_year LIKE '%-%';"))
            conn.execute(text("UPDATE fee_structures SET academic_year = REPLACE(academic_year, '-', '/') WHERE academic_year LIKE '%-%';"))
            conn.execute(text("UPDATE student_fees SET academic_year = REPLACE(academic_year, '-', '/') WHERE academic_year LIKE '%-%';"))
            conn.execute(text("UPDATE exams SET academic_year = REPLACE(academic_year, '-', '/') WHERE academic_year LIKE '%-%';"))
            conn.execute(text("UPDATE timetables SET academic_year = REPLACE(academic_year, '-', '/') WHERE academic_year LIKE '%-%';"))
            conn.execute(text("UPDATE teacher_assignments SET academic_year = REPLACE(academic_year, '-', '/') WHERE academic_year LIKE '%-%';"))
        print("  Academic years normalized.")

        print(">>> 4. Consolidating Grade 8 - A into Canonical Class (ID 32)...")
        c32 = db.query(SchoolClass).filter(SchoolClass.id == 32).first()
        if c32:
            c32.name = "Grade 8 - A"
            c32.code = "G8-A-2026"
            c32.division = "PRIMARY"
            c32.level = "Grade 8"
            c32.section = "A"
            c32.academic_year = "2026/2027"
            c32.status = "ACTIVE"
            c32.capacity = 45

            # Update its enrollments and fee items to 2026/2027
            for en in db.query(StudentEnrollment).filter(StudentEnrollment.class_id == 32).all():
                en.academic_year = "2026/2027"
                en.status = "ACTIVE"
            for fs in db.query(FeeStructure).filter(FeeStructure.class_id == 32).all():
                fs.academic_year = "2026/2027"
            for sf in db.query(StudentFee).filter(StudentFee.class_id == 32).all():
                sf.academic_year = "2026/2027"
            for ex in db.query(Exam).filter(Exam.class_id == 32).all():
                ex.academic_year = "2026/2027"
            for tt in db.query(Timetable).filter(Timetable.class_id == 32).all():
                tt.academic_year = "2026/2027"
            for ta in db.query(TeacherAssignment).filter(TeacherAssignment.class_id == 32).all():
                ta.academic_year = "2026/2027"
            db.commit()
            print("  Class 32 consolidated as canonical Grade 8 - A for 2026/2027.")

        print(">>> 5. Synchronizing Class 1 (Grade 5 - A) Academic Year to 2026/2027...")
        c1 = db.query(SchoolClass).filter(SchoolClass.id == 1).first()
        if c1:
            c1.name = "Grade 5 - A"
            c1.code = "G5-A-2026"
            c1.division = "PRIMARY"
            c1.level = "Grade 5"
            c1.section = "A"
            c1.academic_year = "2026/2027"
            c1.status = "ACTIVE"
            db.commit()
            print("  Class 1 synchronized to 2026/2027.")

        print(">>> 6. Handling invalid secondary classes (59 & 60: Form 5 & 6)...")
        for fid in [59, 60]:
            fc = db.query(SchoolClass).filter(SchoolClass.id == fid).first()
            if fc:
                fc.status = "INACTIVE"
                for en in db.query(StudentEnrollment).filter(StudentEnrollment.class_id == fid).all():
                    en.status = "COMPLETED"
                db.commit()
                print(f"  Marked invalid secondary class ID {fid} ({fc.name}) INACTIVE.")

        print(">>> 7. Removing any remaining duplicate student enrollments in same academic year...")
        from collections import defaultdict
        student_enrs = defaultdict(list)
        for en in db.query(StudentEnrollment).filter(StudentEnrollment.status == "ACTIVE").all():
            student_enrs[(en.student_id, en.academic_year)].append(en)

        for (s_id, yr), elist in student_enrs.items():
            if len(elist) > 1:
                sorted_el = sorted(elist, key=lambda e: (
                    0 if e.school_class and e.school_class.status == "ACTIVE" and "test" not in e.school_class.name.lower() else 1,
                    -e.id
                ))
                canonical_en = sorted_el[0]
                for dup_en in sorted_el[1:]:
                    print(f"  Resolving duplicate enrollment for student {s_id} in {yr}: removing enr {dup_en.id} (class {dup_en.class_id}), keeping {canonical_en.id} (class {canonical_en.class_id})")
                    db.delete(dup_en)
                db.commit()

        print(">>> 8. Ensuring database uniqueness constraint uq_class_academic_year_div_level_sec...")
        with engine.begin() as conn:
            res = conn.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'classes' AND constraint_name = 'uq_class_academic_year_div_level_sec';
            """)).fetchone()
            if not res:
                conn.execute(text("""
                    ALTER TABLE classes 
                    ADD CONSTRAINT uq_class_academic_year_div_level_sec 
                    UNIQUE (academic_year, division, level, section);
                """))
                print("  Constraint uq_class_academic_year_div_level_sec added.")
            else:
                print("  Constraint uq_class_academic_year_div_level_sec already exists.")

        print(">>> 9. Class Consolidation & Cleanup Complete!")
    finally:
        db.close()


if __name__ == "__main__":
    clean_and_consolidate_classes()
