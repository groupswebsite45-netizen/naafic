"""
Data normalization & setup script for Class Promotion acceptance tests.
Ensures classes and enrollments exist for 2026/2027 and 2027/2028 with sections A, B.
"""
from datetime import date
from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment


def normalize_existing_classes(db):
    print("Normalizing existing classes...")
    classes = db.query(SchoolClass).all()
    for c in classes:
        # If name has Form, division must be SECONDARY
        if "form" in c.name.lower():
            if c.division != "SECONDARY":
                c.division = "SECONDARY"
            if not c.level:
                import re
                m = re.search(r"form\s*(\d+)", c.name, re.IGNORECASE)
                if m:
                    c.level = f"Form {m.group(1)}"
        elif "grade" in c.name.lower():
            if c.division != "PRIMARY":
                c.division = "PRIMARY"
            if not c.level:
                import re
                m = re.search(r"grade\s*(\d+)", c.name, re.IGNORECASE)
                if m:
                    c.level = f"Grade {m.group(1)}"
        # Extract section if missing
        if not c.section and " - " in c.name:
            parts = c.name.split(" - ")
            if len(parts) >= 2:
                c.section = parts[1].strip()
    db.commit()
    print("Existing classes normalized.")


def ensure_classes(db):
    print("Ensuring standard classes exist for 2026/2027 and 2027/2028...")
    years = ["2026/2027", "2027/2028"]

    primary_levels = [f"Grade {i}" for i in range(1, 9)]
    secondary_levels = [f"Form {i}" for i in range(1, 5)]

    created_count = 0
    for yr in years:
        clean_yr = yr.replace("/", "-")
        # Primary Grade 1..8 with sections A, B
        for lvl in primary_levels:
            num = lvl.split()[1]
            for sec in ["A", "B"]:
                name = f"{lvl} - {sec}"
                code = f"G{num}-{sec}-{clean_yr}"
                existing = db.query(SchoolClass).filter(
                    (SchoolClass.academic_year == yr) &
                    (SchoolClass.division == "PRIMARY") &
                    (SchoolClass.level == lvl) &
                    (SchoolClass.section == sec)
                ).first()
                if not existing:
                    # check code uniqueness
                    code_exists = db.query(SchoolClass).filter(SchoolClass.code == code).first()
                    if code_exists:
                        code = f"G{num}-{sec}-{clean_yr}-{existing.id if existing else 'NEW'}"
                    c = SchoolClass(
                        name=name,
                        code=code,
                        division="PRIMARY",
                        level=lvl,
                        section=sec,
                        academic_year=yr,
                        capacity=45,
                        status="ACTIVE"
                    )
                    db.add(c)
                    created_count += 1

        # Secondary Form 1..4 with sections A, B
        for lvl in secondary_levels:
            num = lvl.split()[1]
            for sec in ["A", "B"]:
                name = f"{lvl} - {sec}"
                code = f"F{num}-{sec}-{clean_yr}"
                existing = db.query(SchoolClass).filter(
                    (SchoolClass.academic_year == yr) &
                    (SchoolClass.division == "SECONDARY") &
                    (SchoolClass.level == lvl) &
                    (SchoolClass.section == sec)
                ).first()
                if not existing:
                    code_exists = db.query(SchoolClass).filter(SchoolClass.code == code).first()
                    if code_exists:
                        code = f"F{num}-{sec}-{clean_yr}-NEW"
                    c = SchoolClass(
                        name=name,
                        code=code,
                        division="SECONDARY",
                        level=lvl,
                        section=sec,
                        academic_year=yr,
                        capacity=40,
                        status="ACTIVE"
                    )
                    db.add(c)
                    created_count += 1

    db.commit()
    print(f"Created {created_count} standard classes.")


def ensure_students_for_tests(db):
    print("Checking student enrollments for tests...")
    # Find Grade 2A, Grade 4A, Grade 4B, Grade 8A, Form 1B, Form 4A in 2026/2027
    classes_to_populate = [
        ("PRIMARY", "Grade 2", "A", 3),
        ("PRIMARY", "Grade 4", "A", 4),
        ("PRIMARY", "Grade 4", "B", 4),
        ("PRIMARY", "Grade 8", "A", 3),
        ("SECONDARY", "Form 1", "B", 3),
        ("SECONDARY", "Form 4", "A", 3),
    ]

    total_created_students = 0
    for div, lvl, sec, count in classes_to_populate:
        sc = db.query(SchoolClass).filter(
            SchoolClass.academic_year == "2026/2027",
            SchoolClass.division == div,
            SchoolClass.level == lvl,
            SchoolClass.section == sec
        ).first()

        if not sc:
            print(f"Warning: class {lvl} - {sec} not found.")
            continue

        existing_enrs = db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == sc.id,
            StudentEnrollment.academic_year == "2026/2027",
            StudentEnrollment.status == "ACTIVE"
        ).count()

        needed = count - existing_enrs
        if needed > 0:
            for k in range(needed):
                import uuid
                rnd = uuid.uuid4().hex[:6].upper()
                adm = f"ADM-2026-{rnd}"
                student = Student(
                    admission_number=adm,
                    first_name=f"Test{lvl.replace(' ', '')}{sec}",
                    last_name=f"Student{rnd[:3]}",
                    gender="Male" if k % 2 == 0 else "Female",
                    date_of_birth=date(2012, 1, 1),
                    status="ACTIVE"
                )
                db.add(student)
                db.flush()

                enr = StudentEnrollment(
                    student_id=student.id,
                    class_id=sc.id,
                    academic_year="2026/2027",
                    roll_number=f"ROLL-{rnd[:4]}",
                    start_date=date(2026, 9, 1),
                    status="ACTIVE"
                )
                db.add(enr)
                total_created_students += 1

    db.commit()
    print(f"Created {total_created_students} test students.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        normalize_existing_classes(db)
        ensure_classes(db)
        ensure_students_for_tests(db)
        print("Setup complete successfully!")
    finally:
        db.close()
