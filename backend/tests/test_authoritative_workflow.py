import pytest
from datetime import date, datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.user import User
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment

client = TestClient(app)


def get_token_for_user(user: User) -> str:
    return create_access_token(subject=str(user.id))


def test_full_authoritative_result_workflow():
    db = SessionLocal()
    try:
        # Setup: Find users & teachers
        user_admin = db.query(User).filter(User.username == "admin").first()
        user_fadumo = db.query(User).filter(User.username == "teacher.fadumo").first()
        user_ahmed = db.query(User).filter(User.username == "teacher.ahmed").first()
        
        teacher_fadumo = db.query(Teacher).filter(Teacher.id == 19).first()
        teacher_ahmed = db.query(Teacher).filter(Teacher.id == 18).first()

        assert user_admin is not None, "Admin user required"
        assert user_fadumo is not None, "Teacher Fadumo user required"
        assert user_ahmed is not None, "Teacher Ahmed user required"

        token_fadumo = get_token_for_user(user_fadumo)
        token_ahmed = get_token_for_user(user_ahmed)
        token_admin = get_token_for_user(user_admin)

        headers_fadumo = {"Authorization": f"Bearer {token_fadumo}"}
        headers_ahmed = {"Authorization": f"Bearer {token_ahmed}"}
        headers_admin = {"Authorization": f"Bearer {token_admin}"}

        # TEST 1: Teacher Fadumo queries her classes
        # Fadumo is assigned:
        # - English (ID 23) -> Grade 7-A (ID 31)
        # - Somali (ID 22) -> Grade 7-A (ID 31)
        # - English (ID 23) -> Grade 8-A (ID 32)
        # Fadumo is NOT assigned:
        # - Somali (ID 22) -> Grade 8-A (ID 32)
        res1 = client.get("/api/v1/teacher-portal/classes", headers=headers_fadumo)
        assert res1.status_code == 200
        classes_data = res1.json()
        assert len(classes_data) >= 3
        # Verify teacher name is authoritative
        for c in classes_data:
            assert c["teacher_name"] == "Fadumo Mohamed Warsame"
            assert "Moah" not in c["teacher_name"]

        # TEST 2: Teacher Fadumo creates exam for assigned stream (Grade 7-A + Somali)
        exam_payload_valid = {
            "name": "Mid-Term Somali Grade 7-A Test 2025",
            "exam_type": "Mid-Term",
            "academic_year": "2026/2027",
            "class_id": 31,
            "subject_id": 22,
            "start_date": "2025-10-15",
            "max_marks": 100,
            "pass_marks": 50,
            "instructions": "Answer all questions",
        }

        # Check if already exists from prior test runs, if so clean up for isolated test
        old_exam = db.query(Exam).filter(
            Exam.academic_year == "2026/2027",
            Exam.class_id == 31,
            Exam.subject_id == 22,
            Exam.name == exam_payload_valid["name"]
        ).first()
        if old_exam:
            db.delete(old_exam)
            db.commit()

        res2 = client.post("/api/v1/teacher-portal/exams", json=exam_payload_valid, headers=headers_fadumo)
        assert res2.status_code == 201, f"Expected 201, got {res2.status_code}: {res2.text}"
        created_exam = res2.json()
        exam_id = created_exam["id"]
        assert created_exam["teacher_id"] == teacher_fadumo.id

        # TEST 3: Teacher Fadumo attempts to create exam for unassigned class (Grade 8-A + Somali) -> MUST RETURN 403
        exam_payload_invalid = {
            "name": "Mid-Term Somali Grade 8-A Invalid",
            "exam_type": "Mid-Term",
            "academic_year": "2026/2027",
            "class_id": 32,  # Fadumo does NOT teach Somali in Grade 8-A
            "subject_id": 22,
            "start_date": "2025-10-15",
            "max_marks": 100,
            "pass_marks": 50,
        }
        res3 = client.post("/api/v1/teacher-portal/exams", json=exam_payload_invalid, headers=headers_fadumo)
        assert res3.status_code == 403, f"Expected 403 Forbidden for unassigned class/subject, got {res3.status_code}"

        # TEST 4: Teacher Fadumo enters marks and submits results
        # Fetch roster
        res_roster = client.get(f"/api/v1/results/teacher/exams/{exam_id}/roster", headers=headers_fadumo)
        assert res_roster.status_code == 200
        roster_data = res_roster.json()
        students = roster_data["students"]
        assert len(students) > 0

        marks_payload = {
            "exam_id": exam_id,
            "class_id": 31,
            "subject_id": 22,
            "marks": [
                {
                    "student_id": s["student_id"],
                    "attendance_status": "PRESENT",
                    "marks_obtained": 85.0,
                    "remarks": "Excellent"
                }
                for s in students
            ]
        }

        # Save draft first
        res_draft = client.post("/api/v1/results/teacher/draft", json=marks_payload, headers=headers_fadumo)
        assert res_draft.status_code == 200

        # Submit to Admin
        res_submit = client.post("/api/v1/results/teacher/submit", json=marks_payload, headers=headers_fadumo)
        assert res_submit.status_code == 200
        submit_data = res_submit.json()
        assert submit_data["status"] == "SUBMITTED"
        submission_id = submit_data["submission_id"]

        # Verify exactly ONE result_submission exists
        sub_count = db.query(ResultSubmission).filter(
            ResultSubmission.exam_id == exam_id,
            ResultSubmission.class_id == 31,
            ResultSubmission.subject_id == 22,
            ResultSubmission.teacher_id == teacher_fadumo.id
        ).count()
        assert sub_count == 1

        # TEST 5: Admin opens Results Management and verifies submitted result appears
        res_admin_classes = client.get(
            "/api/v1/results/classes",
            params={"academic_year": "2026/2027", "exam_name": exam_payload_valid["name"]},
            headers=headers_admin
        )
        assert res_admin_classes.status_code == 200
        admin_classes = res_admin_classes.json()
        assert len(admin_classes) == 1  # Only Grade 7-A has this exam
        assert admin_classes[0]["class_id"] == 31

        # TEST 6: Verify no fake result cards generated for unrelated classes
        class_ids_in_summary = [c["class_id"] for c in admin_classes]
        assert 33 not in class_ids_in_summary  # Form 1-A has no exam for this series
        assert 34 not in class_ids_in_summary  # Form 2-A has no exam for this series

        # TEST 7: Admin releases the submission
        res_release = client.post(
            f"/api/v1/results/submissions/{submission_id}/release",
            headers=headers_admin
        )
        assert res_release.status_code == 200
        release_data = res_release.json()
        assert release_data["status"] == "RELEASED"

        # Check DB status
        sub_db = db.query(ResultSubmission).filter(ResultSubmission.id == submission_id).first()
        assert sub_db.status == "RELEASED"

        # TEST 8: Student in Grade 7-A can see released result
        # Find enrolled student in Grade 7-A with a portal account
        student_in_class = db.query(Student).join(StudentEnrollment).filter(
            StudentEnrollment.class_id == 31,
            StudentEnrollment.academic_year == "2026/2027",
            Student.user_id.isnot(None)
        ).first()

        if student_in_class and student_in_class.user:
            token_student = get_token_for_user(student_in_class.user)
            res_student = client.get(
                "/api/v1/results/student/my-results",
                headers={"Authorization": f"Bearer {token_student}"}
            )
            assert res_student.status_code == 200
            student_results = res_student.json()
            # Student sees released result
            released_exam_ids = [r["exam_id"] for r in student_results]
            assert exam_id in released_exam_ids

        # TEST 9: Teacher Ahmed cannot submit Teacher Fadumo's exam (IDOR protection)
        res_idor = client.post(
            "/api/v1/results/teacher/submit",
            json=marks_payload,
            headers=headers_ahmed
        )
        assert res_idor.status_code == 403, f"Expected 403 for unauthorized teacher submission, got {res_idor.status_code}"

        # TEST 10: Repeated submit does not create duplicate result_submission
        # Fadumo submitting again should update existing submission, not create duplicates
        # First return to draft to simulate resubmit
        res_return = client.post(
            f"/api/v1/results/submissions/{submission_id}/return",
            json={"reason": "Please check marks"},
            headers=headers_admin
        )
        assert res_return.status_code == 200

        # Resubmit
        res_resubmit = client.post(
            "/api/v1/results/teacher/submit",
            json=marks_payload,
            headers=headers_fadumo
        )
        assert res_resubmit.status_code == 200

        # Verify still exactly ONE submission in DB
        sub_count_after = db.query(ResultSubmission).filter(
            ResultSubmission.exam_id == exam_id,
            ResultSubmission.class_id == 31,
            ResultSubmission.subject_id == 22,
            ResultSubmission.teacher_id == teacher_fadumo.id
        ).count()
        assert sub_count_after == 1

        print("\nAll 10 workflow tests PASSED successfully!")
    finally:
        db.close()
