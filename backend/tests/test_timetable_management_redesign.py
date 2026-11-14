import sys
import os
from datetime import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.timetable import Timetable
from app.models.school_class import SchoolClass
from app.models.teacher import Teacher
from app.models.subject import Subject

client = TestClient(app)

def test_timetable_management_features():
    print("==================================================")
    print("TESTING TIMETABLE MANAGEMENT REDESIGN & CONFLICT ENGINE")
    print("==================================================")

    # 1. Login as Admin
    login_res = client.post("/api/v1/auth/login", json={
        "identifier": "admin",
        "password": "Admin@Hawlwadaag2026"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[OK] Admin authenticated successfully.")

    # 2. Test Timetable Summary
    sum_res = client.get("/api/v1/timetable/summary?academic_year=2026/2027", headers=headers)
    assert sum_res.status_code == 200, f"Summary failed: {sum_res.text}"
    summary = sum_res.json()
    print(f"[OK] Summary retrieved from PostgreSQL: {summary}")
    assert "total_periods" in summary
    assert "scheduled_classes" in summary
    assert "assigned_teachers" in summary
    assert "conflicts_count" in summary
    assert "conflicts" in summary

    # 3. Test Filter Options
    filter_res = client.get("/api/v1/timetable/filter-options", headers=headers)
    assert filter_res.status_code == 200
    filter_options = filter_res.json()
    print(f"[OK] Filter options: {filter_options}")
    assert len(filter_options["academic_years"]) >= 1
    assert len(filter_options["days_of_week"]) >= 5

    # 4. Fetch available Class, Subject, Teacher for testing
    classes_res = client.get("/api/v1/classes?limit=2", headers=headers)
    subjects_res = client.get("/api/v1/subjects?limit=2", headers=headers)
    teachers_res = client.get("/api/v1/teachers?limit=2", headers=headers)

    classes = classes_res.json()
    subjects = subjects_res.json()
    teachers = teachers_res.json()

    assert len(classes) >= 1, "Need at least 1 class in DB"
    assert len(subjects) >= 1, "Need at least 1 subject in DB"
    assert len(teachers) >= 1, "Need at least 1 teacher in DB"

    class1_id = classes[0]["id"]
    class2_id = classes[1]["id"] if len(classes) > 1 else classes[0]["id"]
    subject1_id = subjects[0]["id"]
    subject2_id = subjects[1]["id"] if len(subjects) > 1 else subjects[0]["id"]
    teacher1_id = teachers[0]["id"]
    teacher2_id = teachers[1]["id"] if len(teachers) > 1 else teachers[0]["id"]

    test_day = "Saturday"
    academic_year = "2026/2027"
    test_room = "Test-Lab-909"

    # Clean up any previous test slots on this test day and room
    db = SessionLocal()
    try:
        db.query(Timetable).filter(
            Timetable.day_of_week == test_day,
            Timetable.room == test_room
        ).delete()
        db.commit()
    finally:
        db.close()

    # 5. Create First Valid Timetable Slot (13:00 - 14:00)
    slot1_payload = {
        "class_id": class1_id,
        "subject_id": subject1_id,
        "teacher_id": teacher1_id,
        "academic_year": academic_year,
        "day_of_week": test_day,
        "start_time": "13:00:00",
        "end_time": "14:00:00",
        "room": test_room,
        "status": "ACTIVE"
    }
    create_res1 = client.post("/api/v1/timetable", headers=headers, json=slot1_payload)
    assert create_res1.status_code == 201, f"Create slot 1 failed: {create_res1.text}"
    slot1 = create_res1.json()
    slot1_id = slot1["id"]
    print(f"[OK] Slot 1 created successfully (ID: {slot1_id})")

    # 6. Test Conflict Check Endpoint
    check_payload = {
        "class_id": class1_id,
        "subject_id": subject2_id,
        "teacher_id": teacher2_id,
        "academic_year": academic_year,
        "day_of_week": test_day,
        "start_time": "13:30:00",
        "end_time": "14:30:00",
        "room": "Another Room"
    }
    check_res = client.post("/api/v1/timetable/check-conflict", headers=headers, json=check_payload)
    assert check_res.status_code == 200
    check_data = check_res.json()
    assert check_data["has_conflict"] is True
    assert check_data["conflicts_count"] >= 1
    assert check_data["conflicts"][0]["conflict_type"] == "CLASS"
    print("[OK] Conflict check endpoint accurately identified CLASS overlap.")

    # 7. Test Class Double-Booking Rejection (Exact and overlapping times)
    conflict_class_payload = {
        "class_id": class1_id,
        "subject_id": subject2_id,
        "teacher_id": teacher2_id,
        "academic_year": academic_year,
        "day_of_week": test_day,
        "start_time": "13:30:00",
        "end_time": "14:30:00",
        "room": "Different Room",
        "status": "ACTIVE"
    }
    dup_class_res = client.post("/api/v1/timetable", headers=headers, json=conflict_class_payload)
    assert dup_class_res.status_code == 409, f"Class conflict was not rejected: {dup_class_res.status_code}"
    print("[OK] Backend rejected overlapping Class schedule with HTTP 409 Conflict.")

    # 8. Test Teacher Double-Booking Rejection
    if class1_id != class2_id:
        conflict_teacher_payload = {
            "class_id": class2_id,
            "subject_id": subject2_id,
            "teacher_id": teacher1_id,  # Same teacher
            "academic_year": academic_year,
            "day_of_week": test_day,
            "start_time": "13:00:00",
            "end_time": "14:00:00",
            "room": "Room 500",
            "status": "ACTIVE"
        }
        dup_teacher_res = client.post("/api/v1/timetable", headers=headers, json=conflict_teacher_payload)
        assert dup_teacher_res.status_code == 409, f"Teacher conflict was not rejected: {dup_teacher_res.status_code}"
        print("[OK] Backend rejected overlapping Teacher assignment with HTTP 409 Conflict.")

    # 9. Test Room Double-Booking Rejection
    if class1_id != class2_id:
        conflict_room_payload = {
            "class_id": class2_id,
            "subject_id": subject2_id,
            "teacher_id": teacher2_id,
            "academic_year": academic_year,
            "day_of_week": test_day,
            "start_time": "13:15:00",
            "end_time": "14:15:00",
            "room": test_room,  # Same room
            "status": "ACTIVE"
        }
        dup_room_res = client.post("/api/v1/timetable", headers=headers, json=conflict_room_payload)
        assert dup_room_res.status_code == 409, f"Room conflict was not rejected: {dup_room_res.status_code}"
        print("[OK] Backend rejected overlapping Room booking with HTTP 409 Conflict.")

    # 10. Test Update Timetable Slot
    update_res = client.put(f"/api/v1/timetable/{slot1_id}", headers=headers, json={
        "start_time": "14:00:00",
        "end_time": "15:00:00"
    })
    assert update_res.status_code == 200, f"Update failed: {update_res.text}"
    updated_slot = update_res.json()
    assert updated_slot["start_time"] == "14:00:00"
    print(f"[OK] Timetable slot {slot1_id} updated successfully.")

    # 11. Test Delete Timetable Slot
    del_res = client.delete(f"/api/v1/timetable/{slot1_id}", headers=headers)
    assert del_res.status_code == 200
    print(f"[OK] Timetable slot {slot1_id} deleted successfully.")

    # Verify not found
    get_res = client.get(f"/api/v1/timetable/{slot1_id}", headers=headers)
    assert get_res.status_code == 404
    print("[OK] Verified slot no longer exists in PostgreSQL.")

    print("\n==================================================")
    print("ALL TIMETABLE INTEGRATION TESTS PASSED (100%)")
    print("==================================================")

if __name__ == "__main__":
    test_timetable_management_features()
