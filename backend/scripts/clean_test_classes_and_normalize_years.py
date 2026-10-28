import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from sqlalchemy import text
from app.models.school_class import SchoolClass
from app.models.student_enrollment import StudentEnrollment
from app.models.teacher_assignment import TeacherAssignment
from app.models.timetable import Timetable
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission
from app.models.fee import FeeStructure, StudentFee
from app.models.system_setting import SystemSetting

def run():
    db = SessionLocal()
    print("=== Starting Database Classes Audit & Normalization ===")

    # 1. Clean up ephemeral Timetable Test Classes
    test_classes = db.query(SchoolClass).filter(
        (SchoolClass.name.like("Timetable Test Class%")) | (SchoolClass.code.like("CONF-%"))
    ).all()
    print(f"Found {len(test_classes)} Timetable Test Classes to clean up.")
    for tc in test_classes:
        db.query(Timetable).filter(Timetable.class_id == tc.id).delete()
        db.delete(tc)
    db.commit()
    print("Cleaned up Timetable Test Classes.")

    # 2. Handle overlapping student enrollments before standardizing academic_year
    for old_y, new_y in [("2026-2027", "2026/2027"), ("2025-2026", "2025/2026")]:
        old_enrs = db.query(StudentEnrollment).filter(StudentEnrollment.academic_year == old_y).all()
        for e in old_enrs:
            existing = db.query(StudentEnrollment).filter(
                StudentEnrollment.student_id == e.student_id,
                StudentEnrollment.academic_year == new_y
            ).first()
            if existing:
                print(f"Student {e.student_id} already has enrollment in {new_y} (ID {existing.id}), deleting old enrollment ID {e.id}")
                db.delete(e)
            else:
                e.academic_year = new_y
        db.commit()

        # Handle overlapping teacher assignments
        old_tas = db.query(TeacherAssignment).filter(TeacherAssignment.academic_year == old_y).all()
        for ta in old_tas:
            existing_ta = db.query(TeacherAssignment).filter(
                TeacherAssignment.teacher_id == ta.teacher_id,
                TeacherAssignment.class_id == ta.class_id,
                TeacherAssignment.subject_id == ta.subject_id,
                TeacherAssignment.academic_year == new_y
            ).first()
            if existing_ta:
                db.delete(ta)
            else:
                ta.academic_year = new_y
        db.commit()

        # Standardize other tables
        db.query(SchoolClass).filter(SchoolClass.academic_year == old_y).update({"academic_year": new_y}, synchronize_session=False)
        db.query(Timetable).filter(Timetable.academic_year == old_y).update({"academic_year": new_y}, synchronize_session=False)
        db.query(Exam).filter(Exam.academic_year == old_y).update({"academic_year": new_y}, synchronize_session=False)
        db.query(ResultSubmission).filter(ResultSubmission.academic_year == old_y).update({"academic_year": new_y}, synchronize_session=False)
        db.query(FeeStructure).filter(FeeStructure.academic_year == old_y).update({"academic_year": new_y}, synchronize_session=False)
        db.query(StudentFee).filter(StudentFee.academic_year == old_y).update({"academic_year": new_y}, synchronize_session=False)
        db.commit()
    print("Standardized academic year formats across all tables.")

    # 3. Merge duplicate Grade 7 - A (ID 160) into canonical Grade 7 - A (ID 147)
    c160 = db.query(SchoolClass).filter(SchoolClass.id == 160).first()
    c147 = db.query(SchoolClass).filter(SchoolClass.id == 147).first()
    if c160 and c147:
        print(f"Merging Class ID 160 ({c160.code}) into Class ID 147 ({c147.code})...")
        enrs = db.query(StudentEnrollment).filter(StudentEnrollment.class_id == 160).all()
        for e in enrs:
            existing_e = db.query(StudentEnrollment).filter(
                StudentEnrollment.student_id == e.student_id,
                StudentEnrollment.academic_year == "2026/2027"
            ).first()
            if not existing_e:
                e.class_id = 147
            else:
                existing_e.class_id = 147
                if e.id != existing_e.id:
                    db.delete(e)

        tchas = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == 160).all()
        for ta in tchas:
            existing_ta = db.query(TeacherAssignment).filter(
                TeacherAssignment.teacher_id == ta.teacher_id,
                TeacherAssignment.class_id == 147,
                TeacherAssignment.subject_id == ta.subject_id,
                TeacherAssignment.academic_year == "2026/2027"
            ).first()
            if not existing_ta:
                ta.class_id = 147
            else:
                db.delete(ta)

        exams = db.query(Exam).filter(Exam.class_id == 160).all()
        for ex in exams:
            existing_ex = db.query(Exam).filter(
                Exam.class_id == 147,
                Exam.subject_id == ex.subject_id,
                Exam.academic_year == "2026/2027",
                Exam.name == ex.name
            ).first()
            if not existing_ex:
                ex.class_id = 147
            else:
                results = db.query(ExamResult).filter(ExamResult.exam_id == ex.id).all()
                for r in results:
                    r.exam_id = existing_ex.id
                    r.class_id = 147
                db.delete(ex)

        db.delete(c160)
        db.commit()
        print("Merged Class 160 into 147 successfully.")

    # 4. Merge duplicate Form 1 - A (ID 43) and Grade 9 - A (ID 157, which is Form 1 A)
    c43 = db.query(SchoolClass).filter(SchoolClass.id == 43).first()
    c157 = db.query(SchoolClass).filter(SchoolClass.id == 157).first()
    if c43 and c157:
        print(f"Merging Class ID 43 into Class ID 157 and standardizing to Form 1 - A...")
        enrs = db.query(StudentEnrollment).filter(StudentEnrollment.class_id == 43).all()
        for e in enrs:
            existing_e = db.query(StudentEnrollment).filter(
                StudentEnrollment.student_id == e.student_id,
                StudentEnrollment.academic_year == "2026/2027"
            ).first()
            if not existing_e:
                e.class_id = 157
            else:
                existing_e.class_id = 157
                if e.id != existing_e.id:
                    db.delete(e)
        c43.code = f"F1-A-2026-DEL-{c43.id}"
        db.commit()
        db.delete(c43)
        db.commit()

        c157.name = "Form 1 - A"
        c157.code = "F1-A-2026"
        c157.division = "SECONDARY"
        c157.level = "Form 1"
        c157.section = "A"
        db.commit()
        print("Merged Form 1 - A classes successfully.")

    # 5. Merge duplicate Grade 10 - A (ID 73) into Form 2 - A (ID 34) for 2025/2026
    c73 = db.query(SchoolClass).filter(SchoolClass.id == 73).first()
    c34 = db.query(SchoolClass).filter(SchoolClass.id == 34).first()
    if c73 and c34:
        print("Merging Class ID 73 into Class ID 34...")
        enrs = db.query(StudentEnrollment).filter(StudentEnrollment.class_id == 73).all()
        for e in enrs:
            existing_e = db.query(StudentEnrollment).filter(
                StudentEnrollment.student_id == e.student_id,
                StudentEnrollment.academic_year == "2025/2026"
            ).first()
            if not existing_e:
                e.class_id = 34
            else:
                existing_e.class_id = 34
                if e.id != existing_e.id:
                    db.delete(e)
        tchas = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == 73).all()
        for ta in tchas:
            existing_ta = db.query(TeacherAssignment).filter(
                TeacherAssignment.teacher_id == ta.teacher_id,
                TeacherAssignment.class_id == 34,
                TeacherAssignment.subject_id == ta.subject_id,
                TeacherAssignment.academic_year == "2025/2026"
            ).first()
            if not existing_ta:
                ta.class_id = 34
            else:
                db.delete(ta)
        c73.code = f"G10-A-2025-DEL-{c73.id}"
        db.commit()
        db.delete(c73)
        db.commit()
        print("Merged Grade 10 - A into Form 2 - A successfully.")

    # 6. Standardize Grade 8 - A (ID 146) code if needed
    c146 = db.query(SchoolClass).filter(SchoolClass.id == 146).first()
    if c146 and c146.code == "G8-TST":
        c146.code = "G8-A-2026"
        db.commit()

    # 7. Update academic_year_current system setting to 2026/2027
    setting = db.query(SystemSetting).filter(SystemSetting.key == "academic_year_current").first()
    if setting:
        setting.value = "2026/2027"
    else:
        db.add(SystemSetting(key="academic_year_current", value="2026/2027", description="Current active academic year", is_public=True))
    db.commit()
    print("Updated current academic year setting to 2026/2027.")

    # 8. Ensure PostgreSQL unique constraint on classes table
    try:
        db.execute(text("ALTER TABLE classes ADD CONSTRAINT uq_class_academic_year_div_level_sec UNIQUE (academic_year, division, level, section);"))
        db.commit()
        print("Created unique constraint uq_class_academic_year_div_level_sec on classes table.")
    except Exception as e:
        db.rollback()
        print(f"Unique constraint status: {e}")

    # 9. Print remaining classes summary
    classes = db.query(SchoolClass).order_by(
        SchoolClass.academic_year.desc(),
        SchoolClass.division.asc(),
        SchoolClass.level.asc(),
        SchoolClass.section.asc()
    ).all()
    print(f"\nRemaining Total Classes: {len(classes)}")
    for c in classes:
        enr_cnt = db.query(StudentEnrollment).filter(StudentEnrollment.class_id == c.id, StudentEnrollment.status == "ACTIVE").count()
        tch_cnt = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == c.id, TeacherAssignment.status == "ACTIVE").count()
        print(f"ID: {c.id:<4} | Name: {c.name:<25} | Code: {c.code:<16} | Div: {c.division:<10} | Lvl: {c.level:<8} | Sec: {c.section or '':<2} | Year: {c.academic_year:<10} | Status: {c.status:<8} | Students: {enr_cnt} | Teachers: {tch_cnt}")

    db.close()
    print("=== Database Normalization Complete ===")

if __name__ == "__main__":
    run()
