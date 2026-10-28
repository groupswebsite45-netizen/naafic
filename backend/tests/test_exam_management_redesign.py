import sys
import os
from datetime import date, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.exam import Exam, ExamResult
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass
from app.models.subject import Subject

client = TestClient(app)


def test_exam_management_complete_workflow():
    print("\n==================================================")
    print("TESTING EXAMS & RESULTS MANAGEMENT SYSTEM REDESIGN")
    print("==================================================")

    # 1. Authenticate Admin
    login_res = client.post("/api/v1/auth/login", json={
        "identifier": "admin",
        "password": "Admin@Hawlwadaag2026"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] Admin authenticated successfully.")

    # 2. Test Exam Summary Endpoint (PostgreSQL live data)
    summary_res = client.get("/api/v1/exams/summary?academic_year=2025-2026", headers=headers)
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert "total_exams" in summary
    assert "upcoming_exams" in summary
    assert "completed_exams" in summary
    assert "published_results" in summary
    assert "total_students_assessed" in summary
    print(f"[PASS] Summary retrieved from PostgreSQL: {summary}")

    # 3. Test Filter Options Endpoint
    filter_res = client.get("/api/v1/exams/filter-options", headers=headers)
    assert filter_res.status_code == 200
    filters = filter_res.json()
    assert len(filters["academic_years"]) >= 1
    assert len(filters["classes"]) >= 1
    assert len(filters["subjects"]) >= 1
    print(f"[PASS] Filter options verified: {len(filters['classes'])} classes, {len(filters['subjects'])} subjects.")

    # Find a class with enrolled students for test
    db = SessionLocal()
    try:
        class_with_students = db.query(SchoolClass).join(StudentEnrollment).filter(
            StudentEnrollment.status == "ACTIVE"
        ).first()
        assert class_with_students is not None, "Need at least 1 class with active students"
        test_class_id = class_with_students.id
        test_academic_year = class_with_students.academic_year

        test_subject = db.query(Subject).filter(Subject.status == "ACTIVE").first()
        assert test_subject is not None
        test_subject_id = test_subject.id

        enrolled_students = db.query(Student).join(StudentEnrollment).filter(
            StudentEnrollment.class_id == test_class_id,
            StudentEnrollment.status == "ACTIVE"
        ).all()
        assert len(enrolled_students) >= 1
        test_student = enrolled_students[0]
        test_student_id = test_student.id
    finally:
        db.close()

    # 4. Conflict Check Endpoint
    conflict_payload = {
        "class_id": test_class_id,
        "start_date": str(date.today() + timedelta(days=30)),
        "end_date": str(date.today() + timedelta(days=32)),
    }
    conflict_res = client.post("/api/v1/exams/check-conflict", headers=headers, json=conflict_payload)
    assert conflict_res.status_code == 200
    conflict_data = conflict_res.json()
    assert "has_conflict" in conflict_data
    print(f"[PASS] Conflict check endpoint working: has_conflict={conflict_data['has_conflict']}.")

    # 5. Create Exam with Validation: End date before Start date
    invalid_date_payload = {
        "name": "Invalid Date Exam",
        "exam_type": "Mid-Term",
        "academic_year": test_academic_year,
        "class_id": test_class_id,
        "subject_id": test_subject_id,
        "start_date": "2026-10-20",
        "end_date": "2026-10-10",  # Invalid
        "max_marks": 100,
        "pass_marks": 50,
        "status": "SCHEDULED"
    }
    invalid_res = client.post("/api/v1/exams", headers=headers, json=invalid_date_payload)
    assert invalid_res.status_code == 422, "Expected 422 for end_date < start_date"
    print("[PASS] Backend rejected end_date < start_date with HTTP 422.")

    # 6. Create Exam with Validation: max_marks <= 0 or pass_marks > max_marks
    invalid_marks_payload = {
        "name": "Invalid Marks Exam",
        "exam_type": "Mid-Term",
        "academic_year": test_academic_year,
        "class_id": test_class_id,
        "subject_id": test_subject_id,
        "start_date": "2026-10-20",
        "end_date": "2026-10-25",
        "max_marks": 50,
        "pass_marks": 60,  # pass > max
        "status": "SCHEDULED"
    }
    invalid_marks_res = client.post("/api/v1/exams", headers=headers, json=invalid_marks_payload)
    assert invalid_marks_res.status_code == 422, "Expected 422 for pass_marks > max_marks"
    print("[PASS] Backend rejected pass_marks > max_marks with HTTP 422.")

    # 7. Create Valid Exam
    test_exam_name = "Unit Testing Examination 2026"
    valid_exam_payload = {
        "name": test_exam_name,
        "exam_type": "Mid-Term",
        "academic_year": test_academic_year,
        "class_id": test_class_id,
        "subject_id": test_subject_id,
        "start_date": str(date.today() + timedelta(days=20)),
        "end_date": str(date.today() + timedelta(days=25)),
        "max_marks": 100.0,
        "pass_marks": 50.0,
        "status": "SCHEDULED"
    }
    create_res = client.post("/api/v1/exams", headers=headers, json=valid_exam_payload)
    assert create_res.status_code == 201, f"Create exam failed: {create_res.text}"
    created_exam = create_res.json()
    exam_id = created_exam["id"]
    assert created_exam["name"] == test_exam_name
    print(f"[PASS] Exam created successfully in PostgreSQL (ID: {exam_id}).")

    # 8. Test Exam Profile Endpoint
    profile_res = client.get(f"/api/v1/exams/{exam_id}/profile", headers=headers)
    assert profile_res.status_code == 200
    profile_data = profile_res.json()
    assert "exam" in profile_data
    assert "student_sheet" in profile_data
    assert profile_data["enrolled_count"] >= 1
    print(f"[PASS] Exam profile loaded with {profile_data['enrolled_count']} enrolled students.")

    # 9. Test Mark Validation: Reject marks > max_marks (105 / 100)
    invalid_entry_payload = {
        "exam_id": exam_id,
        "subject_id": test_subject_id,
        "results": [
            {
                "student_id": test_student_id,
                "marks_obtained": 105.0,  # Exceeds 100
                "remarks": "Invalid high mark"
            }
        ]
    }
    invalid_entry_res = client.post(f"/api/v1/exams/{exam_id}/results", headers=headers, json=invalid_entry_payload)
    assert invalid_entry_res.status_code == 422, "Expected 422 for marks exceeding maximum"
    print("[PASS] Backend rejected marks > max_marks (105 / 100) with HTTP 422.")

    # 10. Test Mark Validation: Reject negative marks (-5 / 100)
    negative_entry_payload = {
        "exam_id": exam_id,
        "subject_id": test_subject_id,
        "results": [
            {
                "student_id": test_student_id,
                "marks_obtained": -5.0,  # Negative
                "remarks": "Negative mark"
            }
        ]
    }
    negative_entry_res = client.post(f"/api/v1/exams/{exam_id}/results", headers=headers, json=negative_entry_payload)
    assert negative_entry_res.status_code == 422, "Expected 422 for negative marks"
    print("[PASS] Backend rejected negative mark (-5) with HTTP 422.")

    # 11. Test Mark Validation: Reject non-enrolled student
    non_enrolled_payload = {
        "exam_id": exam_id,
        "subject_id": test_subject_id,
        "results": [
            {
                "student_id": 999999,  # Non-existent/not enrolled
                "marks_obtained": 85.0,
                "remarks": "Phantom student"
            }
        ]
    }
    non_enrolled_res = client.post(f"/api/v1/exams/{exam_id}/results", headers=headers, json=non_enrolled_payload)
    assert non_enrolled_res.status_code == 422
    print("[PASS] Backend rejected non-enrolled student with HTTP 422.")

    # 12. Test Valid Mark Entry and Grade Calculation
    valid_entry_payload = {
        "exam_id": exam_id,
        "subject_id": test_subject_id,
        "results": [
            {
                "student_id": test_student_id,
                "marks_obtained": 88.5,
                "remarks": "Strong analytical ability"
            }
        ]
    }
    entry_res = client.post(f"/api/v1/exams/{exam_id}/results", headers=headers, json=valid_entry_payload)
    assert entry_res.status_code == 201, f"Failed to save results: {entry_res.text}"
    saved_results = entry_res.json()
    assert len(saved_results) == 1
    assert float(saved_results[0]["marks_obtained"]) == 88.5
    assert saved_results[0]["grade"] == "A"
    print(f"[PASS] Marks saved to PostgreSQL. Grade calculated: {saved_results[0]['grade']}.")

    # 13. Test Update Mark (Upsert without duplicate key violation)
    update_entry_payload = {
        "exam_id": exam_id,
        "subject_id": test_subject_id,
        "results": [
            {
                "student_id": test_student_id,
                "marks_obtained": 95.0,  # Updated to A+
                "remarks": "Exceptional improvement"
            }
        ]
    }
    update_entry_res = client.post(f"/api/v1/exams/{exam_id}/results", headers=headers, json=update_entry_payload)
    assert update_entry_res.status_code == 201
    updated_results = update_entry_res.json()
    assert float(updated_results[0]["marks_obtained"]) == 95.0
    assert updated_results[0]["grade"] == "A+"
    print(f"[PASS] Upsert verified without duplicate conflict. Grade updated to {updated_results[0]['grade']}.")

    # 14. Test Publication Safety: cannot publish while SCHEDULED
    pub_premature_res = client.post(f"/api/v1/exams/{exam_id}/publish", headers=headers, json={"publish": True})
    assert pub_premature_res.status_code == 422, "Should not publish SCHEDULED exam without completing it"
    print("[PASS] Publication safety enforced: Cannot publish exam before COMPLETED status.")

    # Transition to COMPLETED
    update_status_res = client.put(f"/api/v1/exams/{exam_id}", headers=headers, json={"status": "ONGOING"})
    assert update_status_res.status_code == 200
    update_status_res2 = client.put(f"/api/v1/exams/{exam_id}", headers=headers, json={"status": "COMPLETED"})
    assert update_status_res2.status_code == 200
    print("[PASS] Exam status transitioned: SCHEDULED -> ONGOING -> COMPLETED.")

    # Publish results
    publish_res = client.post(f"/api/v1/exams/{exam_id}/publish", headers=headers, json={"publish": True})
    assert publish_res.status_code == 200
    assert publish_res.json()["status"] == "PUBLISHED"
    print("[PASS] Exam results published successfully.")

    # 15. Test Student Report Card endpoint
    rc_res = client.get(f"/api/v1/exams/{exam_id}/report-card/{test_student_id}", headers=headers)
    assert rc_res.status_code == 200
    rc = rc_res.json()
    assert "Hawlwadaag" in rc["school_name"]
    assert rc["student"]["id"] == test_student_id
    assert len(rc["subjects"]) >= 1
    assert rc["summary"]["overall_percentage"] >= 90.0
    print(f"[PASS] Report card generated: {rc['student']['full_name']}, Grade: {rc['summary']['overall_grade']}.")

    # 16. Test Unpublish
    unpub_res = client.post(f"/api/v1/exams/{exam_id}/publish", headers=headers, json={"publish": False})
    assert unpub_res.status_code == 200
    assert unpub_res.json()["status"] == "COMPLETED"
    print("[PASS] Exam unpublishing verified successfully.")

    # Clean up test exam
    del_res = client.delete(f"/api/v1/exams/{exam_id}", headers=headers)
    assert del_res.status_code == 200
    print("[PASS] Test exam cleaned up.")
    print("==================================================")
    print("ALL EXAMS MANAGEMENT BACKEND TESTS PASSED!")
    print("==================================================\n")
