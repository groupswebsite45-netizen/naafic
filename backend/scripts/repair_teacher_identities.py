"""
Script to safely repair teacher identities, deactivate invalid assignments,
and normalize academic year formats without deleting real teacher data.
"""
from app.core.database import SessionLocal
from app.models.teacher import Teacher
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role
from app.models.teacher_assignment import TeacherAssignment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from datetime import date

def repair_data():
    db = SessionLocal()
    try:
        print("=== Step 1: Check User 120 (teacher_test_prom) ===")
        user_120 = db.query(User).filter(User.id == 120).first()
        if user_120:
            existing_t = db.query(Teacher).filter(Teacher.user_id == 120).first()
            if not existing_t:
                print("Creating Teacher profile for User 120 (teacher_test_prom)...")
                t_new = Teacher(
                    user_id=120,
                    teacher_number="TCH-PROM-001",
                    first_name="Promotion",
                    last_name="Teacher",
                    gender="Male",
                    email=user_120.email,
                    phone="+252 61 5000120",
                    qualification="B.Ed Educational Assessment",
                    hire_date=date(2025, 1, 1),
                    status="ACTIVE"
                )
                db.add(t_new)
                db.commit()
                db.refresh(t_new)
                print(f"Created Teacher ID {t_new.id} for User 120.")
            else:
                print(f"User 120 already has Teacher ID {existing_t.id}.")

        print("\n=== Step 2: Deactivate invalid assignments referencing inactive classes or subjects ===")
        all_assignments = db.query(TeacherAssignment).all()
        all_classes = {c.id: c for c in db.query(SchoolClass).all()}
        all_subjects = {s.id: s for s in db.query(Subject).all()}
        all_teachers = {t.id: t for t in db.query(Teacher).all()}

        deactivated_count = 0
        for a in all_assignments:
            is_invalid = False
            reasons = []
            if a.teacher_id not in all_teachers or all_teachers[a.teacher_id].status != "ACTIVE":
                is_invalid = True
                reasons.append("Teacher nonexistent or inactive")
            if a.class_id not in all_classes or all_classes[a.class_id].status != "ACTIVE":
                is_invalid = True
                reasons.append(f"Class {a.class_id} nonexistent or inactive")
            if a.subject_id not in all_subjects or all_subjects[a.subject_id].status != "ACTIVE":
                is_invalid = True
                reasons.append(f"Subject {a.subject_id} nonexistent or inactive")

            if is_invalid and a.status == "ACTIVE":
                a.status = "INACTIVE"
                deactivated_count += 1
                print(f"Deactivated Assignment {a.id} (Teacher {a.teacher_id}, Class {a.class_id}, Subject {a.subject_id}): {', '.join(reasons)}")

        db.commit()
        print(f"Total assignments deactivated: {deactivated_count}")

        print("\n=== Step 3: Normalize Academic Year representation in active assignments ===")
        active_assignments = db.query(TeacherAssignment).filter(TeacherAssignment.status == "ACTIVE").all()
        normalized_count = 0
        for a in active_assignments:
            # Standardize '2025-2026' to '2025/2026'
            if "-" in a.academic_year:
                old_yr = a.academic_year
                new_yr = a.academic_year.replace("-", "/")
                # Check for uniqueness collision before updating
                existing_dup = db.query(TeacherAssignment).filter(
                    TeacherAssignment.id != a.id,
                    TeacherAssignment.teacher_id == a.teacher_id,
                    TeacherAssignment.class_id == a.class_id,
                    TeacherAssignment.subject_id == a.subject_id,
                    TeacherAssignment.academic_year == new_yr
                ).first()
                if not existing_dup:
                    a.academic_year = new_yr
                    normalized_count += 1
                    print(f"Normalized Assignment {a.id} academic year: {old_yr} -> {new_yr}")
                else:
                    # Duplicate exists with normalized year, deactivate the hyphenated one
                    a.status = "INACTIVE"
                    print(f"Duplicate found for Assignment {a.id}. Marked hyphenated duplicate as INACTIVE.")

        db.commit()
        print(f"Total assignments normalized: {normalized_count}")

        print("\n=== Data Repair Complete ===")
    finally:
        db.close()

if __name__ == "__main__":
    repair_data()
