import sys
import os

# Ensure backend root in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass
from app.models.user import User
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.fee import StudentFee, FeePayment, FeeStructure
from app.models.exam import Exam, ExamResult
from app.models.attendance import Attendance
from app.models.notification import Notification
from app.models.student_result_view import StudentResultView
from app.models.class_promotion import ClassPromotionBatch, ClassPromotionRecord
from sqlalchemy import func, text

def run_audit():
    db = SessionLocal()
    try:
        print("==================================================")
        print("DATABASE INTEGRITY & ORPHAN AUDIT REPORT")
        print("==================================================")

        # 1. Total Students Count
        total_students = db.query(Student).count()
        print(f"Total Students: {total_students} (Expected: 20)")
        assert total_students == 20, f"Expected exactly 20 students, found {total_students}!"

        # 2. Active, Inactive, Without Class
        active_count = db.query(Student).filter(Student.status == "ACTIVE").count()
        inactive_count = db.query(Student).filter(Student.status != "ACTIVE").count()

        # Check enrollments for academic year 2026/2027
        enrolled_subq = db.query(StudentEnrollment.student_id).filter(
            StudentEnrollment.status == "ACTIVE",
            StudentEnrollment.academic_year == "2026/2027"
        ).distinct()

        without_class = db.query(Student).filter(~Student.id.in_(enrolled_subq)).count()
        print(f"Active Students: {active_count} (Expected: 20)")
        print(f"Inactive / Suspended: {inactive_count} (Expected: 0)")
        print(f"Without Class: {without_class} (Expected: 0)")
        assert active_count == 20
        assert inactive_count == 0
        assert without_class == 0

        # 3. Primary vs Secondary Breakdown
        primary_classes = db.query(SchoolClass).filter(
            SchoolClass.division == "PRIMARY",
            SchoolClass.status == "ACTIVE",
            SchoolClass.academic_year == "2026/2027"
        ).all()
        primary_class_ids = [c.id for c in primary_classes]

        secondary_classes = db.query(SchoolClass).filter(
            SchoolClass.division == "SECONDARY",
            SchoolClass.status == "ACTIVE",
            SchoolClass.academic_year == "2026/2027"
        ).all()
        secondary_class_ids = [c.id for c in secondary_classes]

        primary_students = db.query(StudentEnrollment.student_id).filter(
            StudentEnrollment.class_id.in_(primary_class_ids),
            StudentEnrollment.status == "ACTIVE",
            StudentEnrollment.academic_year == "2026/2027"
        ).distinct().count()

        secondary_students = db.query(StudentEnrollment.student_id).filter(
            StudentEnrollment.class_id.in_(secondary_class_ids),
            StudentEnrollment.status == "ACTIVE",
            StudentEnrollment.academic_year == "2026/2027"
        ).distinct().count()

        print(f"PRIMARY Students: {primary_students} (Expected: 10)")
        print(f"SECONDARY Students: {secondary_students} (Expected: 10)")
        assert primary_students == 10
        assert secondary_students == 10

        # 4. Class Distribution
        print("\n--- Student Distribution per Active Class (2026/2027) ---")
        for c in primary_classes + secondary_classes:
            st_count = db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == c.id,
                StudentEnrollment.status == "ACTIVE",
                StudentEnrollment.academic_year == "2026/2027"
            ).count()
            if st_count > 0:
                print(f"  [{c.id}] {c.name} ({c.division}): {st_count} students")

        # 5. Check Duplicate Active Classes
        print("\n--- Duplicate Active Classes Audit ---")
        dup_classes = db.execute(text("""
            SELECT academic_year, division, level, section, COUNT(*)
            FROM classes
            WHERE status = 'ACTIVE' AND academic_year = '2026/2027'
            GROUP BY academic_year, division, level, section
            HAVING COUNT(*) > 1
        """)).fetchall()
        print(f"Duplicate Active Classes in 2026/2027: {len(dup_classes)} (Expected: 0)")
        assert len(dup_classes) == 0

        # 6. Check Invalid Active Classes
        invalid_classes = db.query(SchoolClass).filter(
            SchoolClass.status == "ACTIVE",
            (
                (SchoolClass.name.ilike("%test%")) |
                (SchoolClass.name.ilike("%12subj%")) |
                (SchoolClass.name.in_(["Form 5", "Form 6", "Timetable Test Class"])) |
                (SchoolClass.level.is_(None))
            )
        ).all()
        print(f"Invalid Active Classes: {len(invalid_classes)} (Expected: 0)")
        assert len(invalid_classes) == 0

        # 7. Orphan Checks
        print("\n--- Referential Integrity & Orphan Audit ---")
        valid_student_ids = [s.id for s in db.query(Student.id).all()]

        orphan_enrs = db.query(StudentEnrollment).filter(~StudentEnrollment.student_id.in_(valid_student_ids)).count()
        orphan_att = db.query(Attendance).filter(~Attendance.student_id.in_(valid_student_ids)).count()
        orphan_exam_res = db.query(ExamResult).filter(~ExamResult.student_id.in_(valid_student_ids)).count()
        orphan_srv = db.query(StudentResultView).filter(~StudentResultView.student_id.in_(valid_student_ids)).count()
        orphan_fees = db.query(StudentFee).filter(~StudentFee.student_id.in_(valid_student_ids)).count()
        orphan_payments = db.query(FeePayment).filter(~FeePayment.student_id.in_(valid_student_ids)).count()
        orphan_notifs = db.query(Notification).filter(Notification.student_id != None, ~Notification.student_id.in_(valid_student_ids)).count()
        orphan_prom = db.query(ClassPromotionRecord).filter(~ClassPromotionRecord.student_id.in_(valid_student_ids)).count()

        print(f"Orphan Student Enrollments: {orphan_enrs} (Expected: 0)")
        print(f"Orphan Attendances: {orphan_att} (Expected: 0)")
        print(f"Orphan Exam Results: {orphan_exam_res} (Expected: 0)")
        print(f"Orphan Student Result Views: {orphan_srv} (Expected: 0)")
        print(f"Orphan Fee Invoices: {orphan_fees} (Expected: 0)")
        print(f"Orphan Fee Payments: {orphan_payments} (Expected: 0)")
        print(f"Orphan Notifications: {orphan_notifs} (Expected: 0)")
        print(f"Orphan Promotion Records: {orphan_prom} (Expected: 0)")

        assert orphan_enrs == 0
        assert orphan_att == 0
        assert orphan_exam_res == 0
        assert orphan_srv == 0
        assert orphan_fees == 0
        assert orphan_payments == 0
        assert orphan_notifs == 0
        assert orphan_prom == 0

        # 8. User Account & Role Audit
        # Check student users
        st_user_ids = set(s.user_id for s in db.query(Student).filter(Student.user_id != None).all())
        all_student_users = db.execute(text("""
            SELECT u.id, u.username, u.full_name
            FROM users u
            JOIN user_roles ur ON ur.user_id = u.id
            JOIN roles r ON r.id = ur.role_id
            WHERE r.name = 'STUDENT'
        """)).fetchall()
        print(f"\nTotal User Accounts with role 'STUDENT': {len(all_student_users)} (Expected: 20)")
        for u in all_student_users:
            assert u.id in st_user_ids, f"Found student user {u.username} not associated with any retained student!"
        print("[OK] All student user accounts map strictly to retained students.")

        # Check Admin & Teacher accounts
        admin_count = db.query(User).filter(User.is_superuser == True).count()
        teacher_count = db.query(Teacher).count()
        teacher_users_count = db.query(Teacher).filter(Teacher.user_id != None).count()
        print(f"Admin Accounts: {admin_count} (Expected: 1)")
        print(f"Teacher Profiles: {teacher_count} (Expected: 23)")
        print(f"Teacher User Accounts: {teacher_users_count} (Expected: 23)")
        assert admin_count >= 1
        assert teacher_count == 23
        assert teacher_users_count == 23

        # 9. List the 20 Retained Students
        print("\n--- Retained 20 Students Verification ---")
        students_all = db.query(Student).order_by(Student.id).all()
        for idx, s in enumerate(students_all, 1):
            ce = s.current_enrollment
            cname = ce.school_class.name if (ce and ce.school_class) else "None"
            div = ce.school_class.division if (ce and ce.school_class) else "None"
            yr = ce.academic_year if ce else "None"
            print(f" {idx:2d}. [{s.id:3d}] {s.admission_number:15s} | {s.full_name:25s} | Class: {cname:15s} ({div}, {yr}) | User: {s.user_id}")

        print("\n==================================================")
        print("[PASSED] ALL 26 REQUIREMENTS AUDIT PASSED 100%!")
        print("==================================================")

    finally:
        db.close()

if __name__ == "__main__":
    run_audit()
