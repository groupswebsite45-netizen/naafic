import sys
sys.path.insert(0, ".")
from app.core.database import SessionLocal
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission
from app.models.student_enrollment import StudentEnrollment
from app.models.student import Student

def run_clean_and_verify():
    db = SessionLocal()
    print("=" * 70)
    print("STARTING DATA AUDIT AND SAFE RELATIONAL CLEANING")
    print("=" * 70)

    # 1. Clean empty orphan test classes
    test_class_patterns = ["CONF-", "CLS-128391", "G7-2EC2EA", "G7-6F3841", "G8-7A6-2026"]
    classes = db.query(SchoolClass).all()
    cleaned_classes = 0
    for c in classes:
        is_test = any(p in c.code for p in test_class_patterns) or "STREAM" in c.name or "A3F1" in c.name or "A444E9" in c.name
        if is_test:
            enr_count = db.query(StudentEnrollment).filter(StudentEnrollment.class_id == c.id).count()
            assign_count = db.query(TeacherAssignment).filter(TeacherAssignment.class_id == c.id).count()
            exam_count = db.query(Exam).filter(Exam.class_id == c.id).count()
            if enr_count == 0 and assign_count == 0 and exam_count == 0:
                print(f"Safely removing unused test class: ID {c.id} | {c.name} | {c.code}")
                db.delete(c)
                cleaned_classes += 1
            else:
                print(f"Skipping class ID {c.id} ({c.name}) - has active associations ({enr_count} students, {assign_count} assigns, {exam_count} exams)")

    db.commit()
    print(f"Cleaned {cleaned_classes} unused test classes.")

    # 2. Normalize Academic Year strings across classes, assignments, exams, submissions
    # Standard format is YYYY/YYYY (e.g., "2025/2026", "2026/2027")
    print("\n--- Normalizing Academic Year formats ---")
    for c in db.query(SchoolClass).all():
        if "-" in c.academic_year:
            c.academic_year = c.academic_year.replace("-", "/")
    
    for a in db.query(TeacherAssignment).all():
        if "-" in a.academic_year:
            a.academic_year = a.academic_year.replace("-", "/")

    for e in db.query(Exam).all():
        if "-" in e.academic_year:
            e.academic_year = e.academic_year.replace("-", "/")

    for s in db.query(ResultSubmission).all():
        if "-" in s.academic_year:
            s.academic_year = s.academic_year.replace("-", "/")

    for enr in db.query(StudentEnrollment).all():
        if "-" in enr.academic_year:
            enr.academic_year = enr.academic_year.replace("-", "/")

    db.commit()
    print("Academic years normalized.")

    # 3. Synchronize Submissions teacher_id with Exam teacher_id
    print("\n--- Auditing Result Submissions & Teacher consistency ---")
    for s in db.query(ResultSubmission).all():
        if s.exam and s.teacher_id != s.exam.teacher_id and s.exam.teacher_id is not None:
            print(f"Synchronizing Sub ID {s.id} teacher_id from {s.teacher_id} to match Exam {s.exam_id} teacher_id {s.exam.teacher_id}")
            s.teacher_id = s.exam.teacher_id
    db.commit()

    # 4. Final verification counts
    print("\n" + "=" * 70)
    print("FINAL DATABASE STATE SUMMARY:")
    print("=" * 70)
    print(f"Teachers: {db.query(Teacher).count()}")
    print(f"Classes: {db.query(SchoolClass).count()}")
    print(f"Subjects: {db.query(Subject).count()}")
    print(f"Active Teacher Assignments: {db.query(TeacherAssignment).filter(TeacherAssignment.status == 'ACTIVE').count()}")
    print(f"Exams: {db.query(Exam).count()}")
    print(f"Result Submissions: {db.query(ResultSubmission).count()}")
    print(f"Exam Results: {db.query(ExamResult).count()}")

    db.close()
    print("\nData audit and verification complete successfully.")

if __name__ == "__main__":
    run_clean_and_verify()
