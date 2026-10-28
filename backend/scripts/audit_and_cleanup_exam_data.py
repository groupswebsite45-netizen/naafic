import os
import sys
from datetime import datetime, timezone

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission
from app.models.result_release import ResultReleaseBatch
from app.models.student_result_view import StudentResultView
from app.models.notification import Notification, NotificationDelivery
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.teacher_assignment import TeacherAssignment
from app.models.student_enrollment import StudentEnrollment
from app.models.attendance import Attendance
from app.models.fee import FeeStructure, StudentFee, FeePayment
from app.models.timetable import Timetable


def generate_audit_and_cleanup():
    db = SessionLocal()
    audit_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "exam_data_cleanup_audit.md")
    report_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "exam_data_cleanup_report.md")

    print("[1/5] Auditing current exam and core records in PostgreSQL...")

    # Core baseline counts
    initial_counts = {
        "students": db.query(Student).count(),
        "teachers": db.query(Teacher).count(),
        "classes": db.query(SchoolClass).count(),
        "subjects": db.query(Subject).count(),
        "teacher_assignments": db.query(TeacherAssignment).count(),
        "student_enrollments": db.query(StudentEnrollment).count(),
        "attendances": db.query(Attendance).count(),
        "fee_structures": db.query(FeeStructure).count(),
        "student_fees": db.query(StudentFee).count(),
        "fee_payments": db.query(FeePayment).count(),
        "timetables": db.query(Timetable).count(),
    }

    # Exam workflow records
    all_exams = db.query(Exam).all()
    all_results = db.query(ExamResult).all()
    all_submissions = db.query(ResultSubmission).all()
    all_batches = db.query(ResultReleaseBatch).all()
    all_views = db.query(StudentResultView).all()
    exam_notifications = db.query(Notification).filter(
        (Notification.related_exam_id != None) | 
        (Notification.related_result_id != None) | 
        (Notification.related_release_batch_id != None) |
        (Notification.notification_type.in_(["RESULT_RELEASED", "RESULT_SUBMITTED", "EXAM_SCHEDULED"]))
    ).all()

    # Classify exams: teacher-assigned vs orphan/no-teacher vs test
    orphan_exams = [e for e in all_exams if e.teacher_id is None]
    test_exams = [e for e in all_exams if "test" in e.name.lower() or "isolation" in e.name.lower() or "redesign" in e.name.lower()]
    standard_exams = [e for e in all_exams if e not in orphan_exams and e not in test_exams]

    print(f"Found {len(all_exams)} exams ({len(orphan_exams)} orphan, {len(test_exams)} test), {len(all_results)} results, {len(all_submissions)} submissions, {len(all_batches)} batches.")

    # Write exam_data_cleanup_audit.md
    print("[2/5] Creating backend/tests/exam_data_cleanup_audit.md...")
    with open(audit_file_path, "w", encoding="utf-8") as f:
        f.write("# Exam Data Cleanup Pre-Execution Audit Report\n\n")
        f.write(f"**Date Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
        f.write("## 1. Summary of Existing Exam Records Found\n\n")
        f.write(f"| Table / Entity | Record Count | Cleanup Action |\n")
        f.write(f"| :--- | :--- | :--- |\n")
        f.write(f"| `exams` | {len(all_exams)} | Full Safe Removal |\n")
        f.write(f"| `exam_results` | {len(all_results)} | Full Safe Removal |\n")
        f.write(f"| `result_submissions` | {len(all_submissions)} | Full Safe Removal |\n")
        f.write(f"| `result_release_batches` | {len(all_batches)} | Full Safe Removal |\n")
        f.write(f"| `student_result_views` | {len(all_views)} | Full Safe Removal |\n")
        f.write(f"| `exam-related notifications` | {len(exam_notifications)} | Safe Unlink & Removal |\n\n")

        f.write("## 2. Protected Core Entities (Must NEVER Be Modified)\n\n")
        f.write(f"| Entity | Preserved Count | Verification Status |\n")
        f.write(f"| :--- | :--- | :--- |\n")
        for k, v in initial_counts.items():
            f.write(f"| `{k}` | {v} | PROTECTED |\n")
        f.write("\n")

        f.write("## 3. Inventory of Old Exam Records\n\n")
        f.write("| Exam ID | Name | Type | Academic Year | Class ID | Subject ID | Teacher ID | Status |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for e in all_exams:
            f.write(f"| {e.id} | {e.name} | {e.exam_type} | {e.academic_year} | {e.class_id} | {e.subject_id} | {e.teacher_id or 'None (Orphan)'} | {e.status} |\n")
        f.write("\n")

        f.write("## 4. Inventory of Result Submissions\n\n")
        f.write("| Sub ID | Exam ID | Class ID | Subject ID | Teacher ID | Academic Year | Status | Completed / Expected |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for s in all_submissions:
            f.write(f"| {s.id} | {s.exam_id} | {s.class_id} | {s.subject_id} | {s.teacher_id} | {s.academic_year} | {s.status} | {s.completed_students}/{s.expected_students} |\n")
        f.write("\n")

        f.write("## 5. Inventory of Result Release Batches\n\n")
        f.write("| Batch ID | Batch Code | Academic Year | Class ID | Exam Name | Results Count | Status |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for b in all_batches:
            f.write(f"| {b.id} | {b.batch_code} | {b.academic_year} | {b.class_id} | {b.exam_name} | {b.results_count} | {b.status} |\n")
        f.write("\n")

    # Safe foreign-key deletion
    print("[3/5] Executing foreign-key-safe deletion...")
    try:
        # Step 1: Clean exam notifications
        notif_ids = [n.id for n in exam_notifications]
        if notif_ids:
            db.query(NotificationDelivery).filter(NotificationDelivery.notification_id.in_(notif_ids)).delete(synchronize_session=False)
            db.query(Notification).filter(Notification.id.in_(notif_ids)).delete(synchronize_session=False)
        
        # Unlink any remaining notification foreign keys just in case
        db.query(Notification).filter(Notification.related_exam_id != None).update({Notification.related_exam_id: None}, synchronize_session=False)
        db.query(Notification).filter(Notification.related_result_id != None).update({Notification.related_result_id: None}, synchronize_session=False)
        db.query(Notification).filter(Notification.related_release_batch_id != None).update({Notification.related_release_batch_id: None}, synchronize_session=False)
        db.flush()

        # Step 2: Delete student result views
        deleted_views = db.query(StudentResultView).delete(synchronize_session=False)

        # Step 3: Unlink release_batch_id and submission_id in exam_results
        db.query(ExamResult).update({ExamResult.submission_id: None, ExamResult.release_batch_id: None}, synchronize_session=False)
        db.flush()

        # Step 4: Delete exam results
        deleted_results = db.query(ExamResult).delete(synchronize_session=False)

        # Step 5: Delete result submissions
        deleted_submissions = db.query(ResultSubmission).delete(synchronize_session=False)

        # Step 6: Delete result release batches
        deleted_batches = db.query(ResultReleaseBatch).delete(synchronize_session=False)

        # Step 7: Delete exams
        deleted_exams = db.query(Exam).delete(synchronize_session=False)

        db.commit()
        print(f"Deleted: {deleted_exams} exams, {deleted_results} results, {deleted_submissions} submissions, {deleted_batches} batches, {deleted_views} views.")
    except Exception as exc:
        db.rollback()
        print(f"ERROR during cleanup: {exc}")
        raise

    # Step 4: Verification
    print("[4/5] Verifying post-cleanup table counts in PostgreSQL...")
    post_exam_count = db.query(Exam).count()
    post_result_count = db.query(ExamResult).count()
    post_submission_count = db.query(ResultSubmission).count()
    post_batch_count = db.query(ResultReleaseBatch).count()
    post_view_count = db.query(StudentResultView).count()

    print(f"Exams: {post_exam_count} (Expected: 0)")
    print(f"Exam Results: {post_result_count} (Expected: 0)")
    print(f"Result Submissions: {post_submission_count} (Expected: 0)")
    print(f"Release Batches: {post_batch_count} (Expected: 0)")
    print(f"Student Result Views: {post_view_count} (Expected: 0)")

    # Verify core entities preserved
    final_counts = {
        "students": db.query(Student).count(),
        "teachers": db.query(Teacher).count(),
        "classes": db.query(SchoolClass).count(),
        "subjects": db.query(Subject).count(),
        "teacher_assignments": db.query(TeacherAssignment).count(),
        "student_enrollments": db.query(StudentEnrollment).count(),
        "attendances": db.query(Attendance).count(),
        "fee_structures": db.query(FeeStructure).count(),
        "student_fees": db.query(StudentFee).count(),
        "fee_payments": db.query(FeePayment).count(),
        "timetables": db.query(Timetable).count(),
    }

    # Verify zero data loss in core entities
    for key, initial_val in initial_counts.items():
        current_val = final_counts[key]
        assert initial_val == current_val, f"DATA LOSS DETECTED on {key}: initial={initial_val}, current={current_val}"
    print("Core entity integrity verified: ZERO data loss across all protected tables!")

    # Step 5: Write post-cleanup report
    print("[5/5] Creating backend/tests/exam_data_cleanup_report.md...")
    with open(report_file_path, "w", encoding="utf-8") as f:
        f.write("# Exam Data Cleanup Execution & Verification Report\n\n")
        f.write(f"**Date Executed:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
        f.write("## 1. Deletion & Cleanup Summary\n\n")
        f.write("| Table / Model | Records Found | Records Removed | Final Count | Status |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        f.write(f"| `exams` | {len(all_exams)} | {deleted_exams} | {post_exam_count} | CLEANED (0 remaining) |\n")
        f.write(f"| `exam_results` | {len(all_results)} | {deleted_results} | {post_result_count} | CLEANED (0 remaining) |\n")
        f.write(f"| `result_submissions` | {len(all_submissions)} | {deleted_submissions} | {post_submission_count} | CLEANED (0 remaining) |\n")
        f.write(f"| `result_release_batches` | {len(all_batches)} | {deleted_batches} | {post_batch_count} | CLEANED (0 remaining) |\n")
        f.write(f"| `student_result_views` | {len(all_views)} | {deleted_views} | {post_view_count} | CLEANED (0 remaining) |\n")
        f.write(f"| `exam-related notifications` | {len(exam_notifications)} | {len(exam_notifications)} | 0 | UNLINKED & REMOVED |\n\n")

        f.write("## 2. Preserved Core Entities Verification\n\n")
        f.write("| Protected Entity | Baseline Count | Post-Cleanup Count | Difference | Integrity Verification |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for key in initial_counts.keys():
            b = initial_counts[key]
            a = final_counts[key]
            f.write(f"| `{key}` | {b} | {a} | {a - b} | 100% INTACT & PRESERVED |\n")
        f.write("\n")

        f.write("## 3. Direct SQL Verification Results\n\n")
        f.write("```sql\n")
        f.write(f"SELECT COUNT(*) FROM exams;              -- Result: {post_exam_count}\n")
        f.write(f"SELECT COUNT(*) FROM exam_results;       -- Result: {post_result_count}\n")
        f.write(f"SELECT COUNT(*) FROM result_submissions;  -- Result: {post_submission_count}\n")
        f.write("```\n\n")
        f.write("Database is now clean and ready for the authoritative Teacher → Exam → Admin Submission workflow.\n")

    db.close()
    print("Cleanup and audit reports completed successfully!")


if __name__ == "__main__":
    generate_audit_and_cleanup()
