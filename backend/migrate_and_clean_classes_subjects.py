import re
from sqlalchemy import text
from app.core.database import SessionLocal, engine
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.student_enrollment import StudentEnrollment
from app.models.teacher_assignment import TeacherAssignment
from app.models.exam import Exam, ExamResult
from app.models.timetable import Timetable
from app.models.attendance import Attendance
from app.models.fee import FeeStructure
from collections import defaultdict

def run_migration():
    print(">>> 1. Adding columns to 'classes' and 'subjects' tables if not present...")
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE classes ADD COLUMN IF NOT EXISTS division VARCHAR(20) DEFAULT 'PRIMARY';"))
        conn.execute(text("ALTER TABLE classes ADD COLUMN IF NOT EXISTS level VARCHAR(50);"))
        conn.execute(text("ALTER TABLE classes ALTER COLUMN section TYPE VARCHAR(50);"))
        conn.execute(text("ALTER TABLE subjects ADD COLUMN IF NOT EXISTS division VARCHAR(20) DEFAULT 'ALL';"))
        conn.execute(text("ALTER TABLE subjects ADD COLUMN IF NOT EXISTS applicable_levels VARCHAR(255);"))

    db = SessionLocal()

    print(">>> 2. Classifying and standardizing existing classes...")
    all_classes = db.query(SchoolClass).order_by(SchoolClass.id).all()
    for c in all_classes:
        name_lower = c.name.lower()
        # Parse division and level
        grade_match = re.search(r'grade\s*(\d+)', name_lower)
        form_match = re.search(r'form\s*(\d+)', name_lower)

        if grade_match:
            g_num = int(grade_match.group(1))
            c.division = "PRIMARY"
            c.level = f"Grade {g_num}"
        elif form_match:
            f_num = int(form_match.group(1))
            c.division = "SECONDARY"
            c.level = f"Form {f_num}"
        else:
            # Fallback
            c.division = "PRIMARY"
            c.level = c.name.split("-")[0].strip()

        # Parse section
        sec = c.section
        if not sec or sec in ("None", "Stream Blue", "Stream Green", "Delta Stream", "Science Stream"):
            # Check if section in code or name
            code_sec_match = re.search(r'-([A-Z])(?:\b|-)', c.code)
            if code_sec_match:
                c.section = code_sec_match.group(1)
            else:
                c.section = "A"
        elif "Section" in sec:
            c.section = sec.replace("Section", "").strip()
        elif "Stream" in sec:
            c.section = sec.replace("Stream", "").strip()

        # Ensure single letter or clean section (e.g. "A", "B")
        if len(c.section) > 5:
            c.section = "A"

        # Standardize academic year format e.g. "2026/2027" -> "2026-2027"
        if "/" in c.academic_year:
            c.academic_year = c.academic_year.replace("/", "-")

    db.commit()

    print(">>> 3. Safely merging duplicate classes per (academic_year, division, level, section)...")
    # Group by (academic_year, division, level, section)
    classes_by_group = defaultdict(list)
    for c in db.query(SchoolClass).order_by(SchoolClass.id).all():
        classes_by_group[(c.academic_year, c.division, c.level, c.section)].append(c)

    for (ay, div, lvl, sec), group in classes_by_group.items():
        if len(group) <= 1:
            # Format canonical class name
            group[0].name = f"{lvl} - {sec}"
            continue

        print(f"Merging {len(group)} duplicates for Year: {ay}, {div}, {lvl}, Sec: {sec} -> IDs: {[c.id for c in group]}")
        # Select canonical class: pick the one with lowest ID or most references
        canonical = sorted(group, key=lambda c: (
            -(db.query(StudentEnrollment).filter(StudentEnrollment.class_id == c.id).count()),
            -(db.query(TeacherAssignment).filter(TeacherAssignment.class_id == c.id).count()),
            c.id
        ))[0]

        canonical.name = f"{lvl} - {sec}"
        clean_code = f"{lvl.replace('Grade ', 'G').replace('Form ', 'F')}-{sec}-{ay[:4]}"
        canonical.code = clean_code

        duplicates = [c for c in group if c.id != canonical.id]

        for dup in duplicates:
            # 1. Move StudentEnrollments if student not already in canonical
            dup_enrs = db.query(StudentEnrollment).filter(StudentEnrollment.class_id == dup.id).all()
            for enr in dup_enrs:
                existing_canon_enr = db.query(StudentEnrollment).filter(
                    StudentEnrollment.student_id == enr.student_id,
                    StudentEnrollment.class_id == canonical.id,
                    StudentEnrollment.academic_year == enr.academic_year
                ).first()
                if existing_canon_enr:
                    db.delete(enr)
                else:
                    enr.class_id = canonical.id

            # 2. Move TeacherAssignments
            dup_tas = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == dup.id).all()
            for ta in dup_tas:
                existing_canon_ta = db.query(TeacherAssignment).filter(
                    TeacherAssignment.teacher_id == ta.teacher_id,
                    TeacherAssignment.class_id == canonical.id,
                    TeacherAssignment.subject_id == ta.subject_id,
                    TeacherAssignment.academic_year == ta.academic_year
                ).first()
                if existing_canon_ta:
                    db.delete(ta)
                else:
                    ta.class_id = canonical.id

            # 3. Move Exams
            dup_exams = db.query(Exam).filter(Exam.class_id == dup.id).all()
            for ex in dup_exams:
                ex.class_id = canonical.id

            # 4. Move Attendance
            dup_att = db.query(Attendance).filter(Attendance.class_id == dup.id).all()
            for att in dup_att:
                att.class_id = canonical.id

            # 5. Move Timetables
            dup_tt = db.query(Timetable).filter(Timetable.class_id == dup.id).all()
            for tt in dup_tt:
                tt.class_id = canonical.id

            # 6. Move FeeStructures
            dup_fees = db.query(FeeStructure).filter(FeeStructure.class_id == dup.id).all()
            for fee in dup_fees:
                fee.class_id = canonical.id

            # Delete the empty duplicate class
            db.delete(dup)

    db.commit()

    print(">>> 4. Cleaning duplicate TeacherAssignment rows...")
    tas = db.query(TeacherAssignment).order_by(TeacherAssignment.id).all()
    seen_ta = set()
    for ta in tas:
        key = (ta.teacher_id, ta.class_id, ta.subject_id, ta.academic_year)
        if key in seen_ta:
            print(f"Deleting duplicate TeacherAssignment ID {ta.id} for {key}")
            db.delete(ta)
        else:
            seen_ta.add(key)
    db.commit()

    print(">>> 5. Standardizing Subjects and Division Curriculum Isolation...")
    # Secondary subjects
    sec_subject_names = ["Physics", "Chemistry", "Biology", "Geography", "History"]
    # Primary subjects
    pri_subject_names = ["Science", "Integrated Science", "Social Studies", "Social Studies & Geography"]
    # Common subjects (Primary & Secondary)
    common_subjects = ["Mathematics", "English", "Somali", "Islamic Studies", "Arabic", "Computer", "Physical Education"]

    subjects = db.query(Subject).all()
    for s in subjects:
        name_clean = s.name.strip()
        # Deactivate obvious test subjects
        if any(tok in name_clean for tok in ["Advanced Astronomy", "TEST-SUB", "SCI-", "Somali Literature 527B23", "G9"]):
            s.status = "INACTIVE"
            continue

        if name_clean in sec_subject_names or "Physics" in name_clean or "Chemistry" in name_clean or "Biology" in name_clean or "History" in name_clean:
            s.division = "SECONDARY"
            s.applicable_levels = "Form 1,Form 2,Form 3,Form 4"
        elif name_clean in pri_subject_names or "Integrated Science" in name_clean:
            s.division = "PRIMARY"
            s.applicable_levels = "Grade 1,Grade 2,Grade 3,Grade 4,Grade 5,Grade 6,Grade 7,Grade 8"
        else:
            s.division = "ALL"
            s.applicable_levels = "Grade 1,Grade 2,Grade 3,Grade 4,Grade 5,Grade 6,Grade 7,Grade 8,Form 1,Form 2,Form 3,Form 4"

    db.commit()

    # Standardize remaining class names
    for c in db.query(SchoolClass).all():
        c.name = f"{c.level} - {c.section}"
        if not c.code or "PROM" in c.code or "CONF" in c.code or "117592" in c.code:
            c.code = f"{c.level.replace('Grade ', 'G').replace('Form ', 'F')}-{c.section}-{c.academic_year[:4]}"

    db.commit()
    print(">>> Migration and cleanup completed successfully!")
    db.close()

if __name__ == "__main__":
    run_migration()
