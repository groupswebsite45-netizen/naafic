import os
import sys
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient

# Add backend to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.core.database import SessionLocal
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission
from app.models.result_release import ResultReleaseBatch
from app.models.notification import Notification
from app.models.user import User
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.core.security import create_access_token

client = TestClient(app)


def get_token(username: str) -> str:
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if not user:
        raise ValueError(f"User {username} not found")
    return create_access_token(data={"sub": str(user.id), "username": user.username})


def test_full_teacher_exam_admin_student_workflow():
    print("\n--- Starting End-to-End Teacher Exam Workflow Test ---")
    db = SessionLocal()

    # 1. Verify clean database state (Zero old exams, results, submissions)
    print("\n[Step 1] Verifying database clean status...")
    assert db.query(Exam).count() == 0, "Expected 0 exams after cleanup"
    assert db.query(ExamResult).count() == 0, "Expected 0 exam results after cleanup"
    assert db.query(ResultSubmission).count() == 0, "Expected 0 submissions after cleanup"
    print("✓ PostgreSQL exam tables are 100% clean.")

    # 2. Authenticate Teacher (Ahmed Hassan Ali - teacher.ahmed)
    print("\n[Step 2] Authenticating Teacher (teacher.ahmed)...")
    teacher_user = db.query(User).filter(User.username == "teacher.ahmed").first()
    assert teacher_user is not None
    teacher = db.query(Teacher).filter(Teacher.user_id == teacher_user.id).first()
    assert teacher is not None
    teacher_token = get_token("teacher.ahmed")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    print(f"✓ Authenticated as Teacher: {teacher.full_name} (ID: {teacher.id})")

    # 3. Test Teacher Exam Options: Subject & Class Scoping
    print("\n[Step 3] Testing /teacher-portal/exam-options scoping...")
    res = client.get("/api/v1/teacher-portal/exam-options", headers=teacher_headers)
    assert res.status_code == 200, res.text
    opts = res.json()
    print("Available Academic Years:", opts["academic_years"])
    print("Assigned Subjects:", [s["name"] for s in opts["subjects"]])

    # Teacher should have Mathematics and Physics, but NOT English/Somali
    assigned_subject_names = [s["name"] for s in opts["subjects"]]
    assert "Mathematics" in assigned_subject_names
    assert "Physics" in assigned_subject_names
    assert "English" not in assigned_subject_names
    assert "Somali" not in assigned_subject_names

    # Test selecting Mathematics (ID 21) -> classes must be Grade 7 - A and Grade 8 - A only
    res_math = client.get(
        f"/api/v1/teacher-portal/exam-options?academic_year={opts['selected_academic_year']}&subject_id=21",
        headers=teacher_headers
    )
    assert res_math.status_code == 200
    math_classes = [c["name"] for c in res_math.json()["classes"]]
    print("Classes for Mathematics:", math_classes)
    assert "Grade 7 - A" in math_classes or "Grade 8 - A" in math_classes
    assert "Form 1 - A" not in math_classes  # Form 1 - A is Physics only for Ahmed!

    # Test selecting Physics (ID 26) -> class must be Form 1 - A only
    res_phys = client.get(
        f"/api/v1/teacher-portal/exam-options?academic_year={opts['selected_academic_year']}&subject_id=26",
        headers=teacher_headers
    )
    assert res_phys.status_code == 200
    phys_classes = [c["name"] for c in res_phys.json()["classes"]]
    print("Classes for Physics:", phys_classes)
    assert "Form 1 - A" in phys_classes
    assert "Grade 7 - A" not in phys_classes
    print("✓ Subject and cascading class options are strictly scoped and de-duplicated.")

    # 4. Test Backend Authorization on Exam Creation (Malicious attempt)
    print("\n[Step 4] Testing Backend Authorization: Reject unauthorized subject/class creation...")
    unauthorized_payload = {
        "name": "Hacked English Exam",
        "exam_type": "Mid-Term",
        "academic_year": opts["selected_academic_year"],
        "class_id": 31,  # Grade 7 - A
        "subject_id": 54,  # English (Ahmed is NOT assigned English)
        "start_date": "2026-10-15",
        "max_marks": 100,
        "pass_marks": 50,
    }
    res_unauth = client.post("/api/v1/teacher-portal/exams", json=unauthorized_payload, headers=teacher_headers)
    assert res_unauth.status_code == 403
    assert "Teacher is not assigned to this subject and class" in res_unauth.json()["detail"]
    print("✓ Unauthorized exam creation rejected with 403 Forbidden.")

    # 5. Legitimate Exam Creation
    print("\n[Step 5] Creating fresh legitimate examination as Teacher...")
    # Select Grade 7 - A (ID 31) and Mathematics (ID 21)
    legit_payload = {
        "name": "Mid-Term Mathematics Examination 2026",
        "exam_type": "Mid-Term",
        "academic_year": opts["selected_academic_year"],
        "class_id": 31,
        "subject_id": 21,
        "start_date": "2026-10-20",
        "max_marks": 100,
        "pass_marks": 50,
        "instructions": "Answer all questions cleanly in blue or black pen."
    }
    res_create = client.post("/api/v1/teacher-portal/exams", json=legit_payload, headers=teacher_headers)
    assert res_create.status_code == 201, res_create.text
    exam_data = res_create.json()
    exam_id = exam_data["id"]
    print(f"✓ Exam created successfully: ID={exam_id}, Title='{exam_data['name']}'")

    # Verify PostgreSQL records
    created_exam = db.query(Exam).filter(Exam.id == exam_id).first()
    assert created_exam is not None
    assert created_exam.teacher_id == teacher.id
    assert created_exam.class_id == 31
    assert created_exam.subject_id == 21

    created_sub = db.query(ResultSubmission).filter(ResultSubmission.exam_id == exam_id).first()
    assert created_sub is not None
    assert created_sub.status == "DRAFT"
    assert created_sub.teacher_id == teacher.id
    print("✓ Verified PostgreSQL exam and draft ResultSubmission records.")

    # 6. Test Duplicate Exam Prevention
    print("\n[Step 6] Testing Duplicate Exam Prevention...")
    res_dup = client.post("/api/v1/teacher-portal/exams", json=legit_payload, headers=teacher_headers)
    assert res_dup.status_code == 409, "Expected 409 Conflict on duplicate exam"
    print("✓ Duplicate exam attempt blocked with 409 Conflict.")

    # 7. Teacher Exam List Scoping
    print("\n[Step 7] Testing Teacher Exam List isolation...")
    res_list = client.get("/api/v1/teacher-portal/exams", headers=teacher_headers)
    assert res_list.status_code == 200
    my_exams = res_list.json()
    assert len(my_exams) == 1
    assert my_exams[0]["id"] == exam_id

    # Another teacher should see 0 exams
    other_token = get_token("teacher.ali")
    other_headers = {"Authorization": f"Bearer {other_token}"}
    res_other = client.get("/api/v1/teacher-portal/exams", headers=other_headers)
    assert res_other.status_code == 200
    assert len(res_other.json()) == 0
    print("✓ Verified Teacher Exam List isolation (other teachers cannot see Ahmed's exam).")

    # 8. Fetch Roster & Verify Student Enrollment Scoping
    print("\n[Step 8] Fetching student roster for exam...")
    res_roster = client.get(f"/api/v1/teacher-portal/exams/{exam_id}/roster", headers=teacher_headers)
    assert res_roster.status_code == 200
    roster = res_roster.json()
    students = roster["students"]
    print(f"Enrolled students in exam roster: {len(students)}")
    assert len(students) > 0

    # Verify all students belong to Class 31
    enrolled_in_class_31 = db.query(StudentEnrollment).filter(
        StudentEnrollment.class_id == 31,
        StudentEnrollment.status == "ACTIVE"
    ).all()
    enrolled_sids = {e.student_id for e in enrolled_in_class_31}
    for s in students:
        assert s["student_id"] in enrolled_sids, f"Student {s['student_id']} does not belong to class 31"
    print("✓ All students strictly belong to the exam's assigned class.")

    # 9. Enter Marks & Save Draft
    print("\n[Step 9] Saving Draft Marks...")
    marks_list = []
    base_mark = 65.0
    for idx, s in enumerate(students):
        score = base_mark + (idx * 5.0)
        if score > 100.0:
            score = 95.0
        marks_list.append({
            "student_id": s["student_id"],
            "attendance_status": "PRESENT",
            "marks_obtained": score,
            "remarks": "Good performance"
        })

    draft_payload = {
        "exam_id": exam_id,
        "class_id": 31,
        "subject_id": 21,
        "marks": marks_list
    }
    res_draft = client.post(f"/api/v1/teacher-portal/exams/{exam_id}/draft", json={"results": marks_list}, headers=teacher_headers)
    assert res_draft.status_code == 200, res_draft.text
    print("✓ Draft marks saved successfully.")

    # 10. Submit Results to Administration
    print("\n[Step 10] Submitting results to Administration...")
    res_submit = client.post(
        f"/api/v1/teacher-portal/exams/{exam_id}/submit",
        json={"results": marks_list, "confirmation_notes": "Submitted after complete grading"},
        headers=teacher_headers
    )
    assert res_submit.status_code == 200, res_submit.text
    submit_data = res_submit.json()
    assert submit_data["status"] == "SUBMITTED"
    assert "Results submitted successfully to Administration." in submit_data["message"]
    print("✓ Results submitted. Confirmation received:", submit_data["message"])

    # Verify PostgreSQL submission record
    sub_record = db.query(ResultSubmission).filter(ResultSubmission.exam_id == exam_id).first()
    assert sub_record.status == "SUBMITTED"
    assert sub_record.submitted_at is not None
    assert sub_record.submitted_by_id == teacher_user.id
    print("✓ PostgreSQL submission status is SUBMITTED with timestamp and submitted_by.")

    # Verify Admin Notification was created in PostgreSQL
    notif = db.query(Notification).filter(Notification.related_exam_id == exam_id).first()
    assert notif is not None
    assert notif.notification_type == "RESULT_SUBMITTED"
    assert notif.title == "New examination results submitted"
    print(f"✓ Verified Admin Notification in PostgreSQL: '{notif.title}'")

    # 11. Test Duplicate Submission Prevention
    print("\n[Step 11] Testing Duplicate Submission Prevention...")
    res_sub_dup = client.post(
        f"/api/v1/teacher-portal/exams/{exam_id}/submit",
        json={"results": marks_list},
        headers=teacher_headers
    )
    assert res_sub_dup.status_code == 409, "Expected 409 Conflict on re-submitting already submitted results"
    assert "Results have already been submitted." in res_sub_dup.json()["detail"]
    print("✓ Duplicate submission blocked with 409 Conflict.")

    # 12. Authenticate Admin & Verify Admin Views
    print("\n[Step 12] Authenticating Admin (admin)...")
    admin_token = get_token("admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Admin sees the exam under /api/v1/exams
    res_admin_exams = client.get("/api/v1/exams", headers=admin_headers)
    assert res_admin_exams.status_code == 200
    all_admin_exams = res_admin_exams.json()
    assert any(e["id"] == exam_id for e in all_admin_exams)
    print("✓ Admin sees the teacher-created exam in /api/v1/exams.")

    # Admin sees the submission under /api/v1/results/submissions
    res_admin_subs = client.get("/api/v1/results/submissions", headers=admin_headers)
    assert res_admin_subs.status_code == 200
    all_subs = res_admin_subs.json()
    admin_sub = next((s for s in all_subs if s["exam_id"] == exam_id), None)
    assert admin_sub is not None
    assert admin_sub["status"] == "SUBMITTED"
    assert admin_sub["teacher_name"] == teacher.full_name
    assert admin_sub["completed_students"] == len(students)
    print(f"✓ Admin sees submission in /api/v1/results/submissions: {admin_sub['completed_students']}/{admin_sub['expected_students']} completed, Status={admin_sub['status']}.")

    # 13. Test Admin Read-Only Mark Enforcement (Admin cannot modify marks)
    print("\n[Step 13] Testing Admin Read-Only: Reject Admin attempt to edit marks...")
    res_admin_edit = client.post(
        f"/api/v1/exams/{exam_id}/results",
        json={"results": [{"student_id": students[0]["student_id"], "marks_obtained": 99.0}]},
        headers=admin_headers
    )
    assert res_admin_edit.status_code == 403, "Expected 403 Forbidden when Admin attempts to enter marks"
    print("✓ Admin mark editing strictly rejected with 403 Forbidden.")

    # 14. Test Return for Correction Workflow
    print("\n[Step 14] Testing Admin Return for Correction...")
    sub_id = admin_sub["id"]
    return_payload = {"reason": "Please double check the marks for Student #1"}
    res_return = client.post(f"/api/v1/results/submissions/{sub_id}/return", json=return_payload, headers=admin_headers)
    assert res_return.status_code == 200
    assert res_return.json()["status"] == "RETURNED"

    # Verify Teacher sees RETURNED status
    res_teacher_roster = client.get(f"/api/v1/teacher-portal/exams/{exam_id}/roster", headers=teacher_headers)
    assert res_teacher_roster.json()["submission_status"] == "RETURNED"
    assert res_teacher_roster.json()["return_reason"] == return_payload["reason"]
    print(f"✓ Submission marked RETURNED. Reason visible to teacher: '{res_teacher_roster.json()['return_reason']}'")

    # Teacher modifies student mark and resubmits
    marks_list[0]["marks_obtained"] = 98.0
    res_resubmit = client.post(
        f"/api/v1/teacher-portal/exams/{exam_id}/submit",
        json={"results": marks_list},
        headers=teacher_headers
    )
    assert res_resubmit.status_code == 200
    assert res_resubmit.json()["status"] == "SUBMITTED"
    print("✓ Teacher successfully edited and resubmitted results. Status is now SUBMITTED again.")

    # 15. Test Student Visibility Before Release (Must be invisible)
    print("\n[Step 15] Testing Student Visibility: Results hidden before release...")
    first_student_id = students[0]["student_id"]
    student_obj = db.query(Student).filter(Student.id == first_student_id).first()
    student_user = db.query(User).filter(User.id == student_obj.user_id).first()
    student_token = get_token(student_user.username)
    student_headers = {"Authorization": f"Bearer {student_token}"}

    res_std_before = client.get("/api/v1/results/student/my-results", headers=student_headers)
    assert res_std_before.status_code == 200
    # Before release, student should see 0 results for this exam
    assert not any(r["exam_id"] == exam_id for r in res_std_before.json())
    print("✓ Confirmed: Student CANNOT see unreleased results.")

    # 16. Test Admin Release Workflow
    print("\n[Step 16] Admin Releases Results...")
    res_release = client.post(f"/api/v1/results/submissions/{sub_id}/release", headers=admin_headers)
    assert res_release.status_code == 200
    assert res_release.json()["status"] == "RELEASED"
    print(f"✓ Results released by Admin: Batch Code = {res_release.json()['batch_code']}")

    # 17. Test Student Visibility After Release
    print("\n[Step 17] Testing Student Visibility After Release...")
    res_std_after = client.get("/api/v1/results/student/my-results", headers=student_headers)
    assert res_std_after.status_code == 200
    my_results = res_std_after.json()
    assert any(r["exam_id"] == exam_id for r in my_results)
    std_result = next(r for r in my_results if r["exam_id"] == exam_id)
    assert float(std_result["marks_obtained"]) == 98.0
    print(f"✓ Student sees released result: Subject={std_result['subject_name']}, Marks={std_result['marks_obtained']}")

    # 18. Final Database Referencing Integrity Checks
    print("\n[Step 18] Verifying PostgreSQL Referential Integrity...")
    db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
    assert db_exam.teacher_id == teacher.id
    assert db_exam.status == "PUBLISHED"

    db_sub = db.query(ResultSubmission).filter(ResultSubmission.exam_id == exam_id).first()
    assert db_sub.status == "RELEASED"
    assert db_sub.exam_id == db_exam.id

    db_results = db.query(ExamResult).filter(ExamResult.exam_id == exam_id).all()
    assert len(db_results) == len(students)
    for r in db_results:
        assert r.status == "RELEASED"
        assert r.class_id == 31
        assert r.student_id in enrolled_sids

    # Verify no orphan records
    orphan_exams = db.query(Exam).filter(Exam.teacher_id == None).count()
    assert orphan_exams == 0
    orphan_results = db.query(ExamResult).filter(ExamResult.exam_id == None).count()
    assert orphan_results == 0

    db.close()
    print("\n=======================================================")
    print("ALL 18 END-TO-END WORKFLOW & AUTHORIZATION TESTS PASSED!")
    print("=======================================================\n")


if __name__ == "__main__":
    test_full_teacher_exam_admin_student_workflow()
