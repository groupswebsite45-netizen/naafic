import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.timetable import Timetable
from app.models.school_class import SchoolClass
from app.models.teacher import Teacher
from app.models.subject import Subject
from app.models.teacher_assignment import TeacherAssignment
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.user import User

client = TestClient(app)

def test_complete_automated_timetable_system():
    print("\n========================================================")
    print("TESTING COMPLETE AUTOMATED TIMETABLE MANAGEMENT SYSTEM")
    print("========================================================")

    # 1. Authenticate Admin
    login_res = client.post("/api/v1/auth/login", json={
        "identifier": "admin",
        "password": "Admin@Hawlwadaag2026"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] 1. Admin authenticated successfully.")

    # 2. Inspect active classes with teacher assignments
    db = SessionLocal()
    try:
        # Find a class with assignments in 2026/2027 or 2026/2027
        target_assignment = (
            db.query(TeacherAssignment)
            .filter(TeacherAssignment.status == "ACTIVE")
            .first()
        )
        assert target_assignment is not None, "At least one active TeacherAssignment required in test DB"
        class_id = target_assignment.class_id
        teacher_id = target_assignment.teacher_id
        subject_id = target_assignment.subject_id
        academic_year = target_assignment.academic_year or "2026/2027"
        school_class = db.query(SchoolClass).filter(SchoolClass.id == class_id).first()
        class_name = school_class.name if school_class else f"Class {class_id}"
        print(f"[PASS] 2. Target test class: {class_name} (ID: {class_id}), Academic Year: {academic_year}")
    finally:
        db.close()

    # 3. Test Class-First Overview API
    overview_res = client.get(
        f"/api/v1/timetable/class-overview/{class_id}?academic_year={academic_year}",
        headers=headers
    )
    assert overview_res.status_code == 200, f"Class overview failed: {overview_res.text}"
    overview_data = overview_res.json()
    print(f"[PASS] 3. Retrieved class overview with {len(overview_data['assigned_subjects'])} assigned subjects.")
    assert "class_id" in overview_data
    assert "assigned_subjects" in overview_data
    assert len(overview_data["assigned_subjects"]) >= 1

    # 4. Test Teacher Availability API
    avail_payload = {
        "teacher_id": teacher_id,
        "academic_year": academic_year,
        "availabilities": [
            {
                "day_of_week": "Saturday",
                "is_available": True,
                "start_time": "07:30:00",
                "end_time": "13:30:00",
                "max_periods_per_day": 5,
                "notes": "Full day availability"
            },
            {
                "day_of_week": "Sunday",
                "is_available": True,
                "start_time": "07:30:00",
                "end_time": "13:30:00",
                "max_periods_per_day": 5
            },
            {
                "day_of_week": "Friday",
                "is_available": False,
                "notes": "Weekend"
            }
        ]
    }
    avail_save_res = client.post(
        "/api/v1/timetable/teacher-availability",
        headers=headers,
        json=avail_payload
    )
    assert avail_save_res.status_code == 200, f"Save availability failed: {avail_save_res.text}"
    print(f"[PASS] 4. Teacher availability saved: {avail_save_res.json()}")

    get_avail_res = client.get(
        f"/api/v1/timetable/teacher-availability/{teacher_id}?academic_year={academic_year}",
        headers=headers
    )
    assert get_avail_res.status_code == 200
    avail_records = get_avail_res.json()
    assert len(avail_records) >= 3
    print(f"[PASS] 4b. Teacher availability retrieved successfully ({len(avail_records)} days configured).")

    # 5. Test Timetable Generation Engine
    # Build distribution map from assigned subjects
    dist_map = {}
    for s in overview_data["assigned_subjects"]:
        dist_map[s["subject_name"]] = 3  # 3 lessons per week each

    gen_payload = {
        "class_id": class_id,
        "academic_year": academic_year,
        "school_days": ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday"],
        "start_time": "07:30",
        "end_time": "13:00",
        "period_duration_minutes": 45,
        "break_duration_minutes": 20,
        "lunch_duration_minutes": 30,
        "periods_per_day": 5,
        "subject_lessons_distribution": dist_map,
        "respect_teacher_availability": True,
        "overwrite_existing": True
    }
    gen_res = client.post("/api/v1/timetable/generate", headers=headers, json=gen_payload)
    assert gen_res.status_code == 200, f"Generation failed: {gen_res.text}"
    gen_data = gen_res.json()
    print(f"[PASS] 5. Automated Generation: {gen_data['message']}")
    print(f"         Total slots generated: {gen_data['total_slots_generated']}")
    assert gen_data["success"] is True
    assert gen_data["total_slots_generated"] > 0
    assert len(gen_data["slots"]) > 0

    # Verify slots have valid structure (period_number, is_break, day_of_week)
    teaching_slots = [s for s in gen_data["slots"] if not s.get("is_break")]
    break_slots = [s for s in gen_data["slots"] if s.get("is_break")]
    print(f"         Teaching slots: {len(teaching_slots)}, Break slots: {len(break_slots)}")
    assert len(teaching_slots) >= 1

    # 6. Test 10-Point Conflict Validation Engine
    val_res = client.get(
        f"/api/v1/timetable/validate?academic_year={academic_year}&class_id={class_id}",
        headers=headers
    )
    assert val_res.status_code == 200, f"Validation failed: {val_res.text}"
    val_data = val_res.json()
    print(f"[PASS] 6. Timetable Validation: is_valid={val_data['is_valid']}, conflicts={val_data['total_conflicts']}")
    assert val_data["is_valid"] is True, f"Generated timetable should be conflict-free: {val_data['conflicts']}"

    # 7. Test Timetable Publication Lifecycle (Draft -> Published -> Live)
    pub_res = client.post(
        "/api/v1/timetable/publish",
        headers=headers,
        json={"class_id": class_id, "academic_year": academic_year}
    )
    assert pub_res.status_code == 200, f"Publish failed: {pub_res.text}"
    pub_data = pub_res.json()
    print(f"[PASS] 7. Publication success: {pub_data['message']} ({pub_data['published_count']} slots published)")
    assert pub_data["published_count"] > 0

    # 8. Test Class Timetable PDF Generation
    pdf_class_res = client.get(
        f"/api/v1/timetable/pdf/class/{class_id}?academic_year={academic_year}",
        headers=headers
    )
    assert pdf_class_res.status_code == 200, f"Class PDF failed: {pdf_class_res.text}"
    assert pdf_class_res.headers.get("content-type") == "application/pdf"
    assert len(pdf_class_res.content) > 1000
    print(f"[PASS] 8. Class Timetable PDF generated: size={len(pdf_class_res.content)} bytes")

    # 9. Test Teacher Timetable PDF Generation
    pdf_teach_res = client.get(
        f"/api/v1/timetable/pdf/teacher/{teacher_id}?academic_year={academic_year}",
        headers=headers
    )
    assert pdf_teach_res.status_code == 200, f"Teacher PDF failed: {pdf_teach_res.text}"
    assert pdf_teach_res.headers.get("content-type") == "application/pdf"
    assert len(pdf_teach_res.content) > 1000
    print(f"[PASS] 9. Teacher Timetable PDF generated: size={len(pdf_teach_res.content)} bytes")

    # 10. Test Multi-School Data Isolation & RBAC
    # Unauthenticated request must return 401
    unauth_res = client.post("/api/v1/timetable/generate", json=gen_payload)
    assert unauth_res.status_code in [401, 403], f"Unauthenticated generation must be blocked: {unauth_res.status_code}"
    print("[PASS] 10. Security: Unauthenticated access blocked (HTTP 401/403).")

    print("\n========================================================")
    print("ALL 10 AUTOMATED TIMETABLE SYSTEM TESTS PASSED CLEANLY!")
    print("========================================================")

if __name__ == "__main__":
    test_complete_automated_timetable_system()
