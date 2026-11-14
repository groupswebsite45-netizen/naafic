import sys
import os
import random

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.school_class import SchoolClass
from app.models.subject import Subject

client = TestClient(app)

def test_teacher_management_features():
    print("==================================================")
    print("TESTING TEACHER MANAGEMENT REDESIGN & DATABASE INTEGRATION")
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

    # 2. Test Teacher Summary Metrics from PostgreSQL
    summary_res = client.get("/api/v1/teachers/summary", headers=headers)
    assert summary_res.status_code == 200, f"Summary failed: {summary_res.text}"
    summary = summary_res.json()
    print(f"[OK] Summary retrieved from PostgreSQL: {summary}")
    assert "total_teachers" in summary
    assert "active_teachers" in summary
    assert "inactive_teachers" in summary
    assert "unassigned_teachers" in summary
    assert summary["total_teachers"] >= 1

    # 3. Test Teacher Filtering (Search, Status)
    search_res = client.get("/api/v1/teachers?query=Ahmed", headers=headers)
    assert search_res.status_code == 200
    search_items = search_res.json()
    print(f"[OK] Search 'Ahmed' returned {len(search_items)} teachers.")
    assert len(search_items) >= 1

    # Filter by Status 'ACTIVE'
    active_res = client.get("/api/v1/teachers?status=ACTIVE", headers=headers)
    assert active_res.status_code == 200
    active_items = active_res.json()
    print(f"[OK] Status 'ACTIVE' filter returned {len(active_items)} teachers.")
    for item in active_items:
        assert item["status"].upper() == "ACTIVE"

    # 4. Test Teacher Creation with Portal & Initial Assignment
    rand_num = random.randint(100000, 999999)
    # Fetch an existing class and subject
    classes_res = client.get("/api/v1/classes", headers=headers)
    classes = classes_res.json()
    target_class = classes[0] if len(classes) > 0 else None
    class_id = target_class["id"] if target_class else None

    subjects_res = client.get("/api/v1/subjects", headers=headers)
    subjects = subjects_res.json()
    target_subject = subjects[0] if len(subjects) > 0 else None
    subject_id = target_subject["id"] if target_subject else None

    create_payload = {
        "first_name": "Mustaf",
        "middle_name": "Hassan",
        "last_name": "Farah",
        "gender": "Male",
        "date_of_birth": "1992-04-10",
        "phone": f"+25261{rand_num}",
        "email": f"mustaf_{rand_num}@hawlwadaag.edu.so",
        "address": "Hawlwadaag District, Mogadishu",
        "teacher_number": f"TCH-{rand_num}",
        "qualification": "M.Sc. Mathematics Education",
        "hire_date": "2026-09-01",
        "status": "ACTIVE",
        "create_portal_account": True,
        "portal_username": f"mustaf_{rand_num}",
        "portal_password": "Teacher@Hawlwadaag2026"
    }

    create_res = client.post("/api/v1/teachers", json=create_payload, headers=headers)
    assert create_res.status_code == 201, f"Teacher creation failed: {create_res.text}"
    created_teacher = create_res.json()
    teacher_id = created_teacher["id"]
    print(f"[OK] Created new teacher: {created_teacher['full_name']} (ID: {teacher_id}, TCH ID: {created_teacher['teacher_number']})")
    assert created_teacher["has_portal_access"] is True

    # 5. Test Full Teacher Profile Retrieval
    profile_res = client.get(f"/api/v1/teachers/{teacher_id}/full", headers=headers)
    assert profile_res.status_code == 200, f"Full Profile failed: {profile_res.text}"
    profile = profile_res.json()
    print(f"[OK] Full Profile retrieved: {profile['full_name']} | Qualification: {profile['qualification']} | Assignments count: {len(profile.get('assignments', []))}")
    assert profile["teacher_number"] == f"TCH-{rand_num}"
    assert "assignments" in profile
    assert "timetables" in profile

    # 6. Test Additional Assignment Allocation and Duplicate Prevention
    if class_id and subject_id:
        test_academic_year = f"20{30 + (rand_num % 40)}-20{31 + (rand_num % 40)}"
        assign_payload = {
            "class_id": class_id,
            "subject_id": subject_id,
            "academic_year": test_academic_year
        }
        # First assignment
        assign_res = client.post(f"/api/v1/teachers/{teacher_id}/assignments", json=assign_payload, headers=headers)
        assert assign_res.status_code == 201, f"Initial assignment failed: {assign_res.text}"
        print("[OK] Teacher assigned to class and subject successfully.")

        # Attempting duplicate assignment should be rejected (400 or 409)
        dup_res = client.post(f"/api/v1/teachers/{teacher_id}/assignments", json=assign_payload, headers=headers)
        assert dup_res.status_code in [400, 409], f"Duplicate assignment check failed: {dup_res.status_code}"
        print("[OK] Duplicate class-subject assignment properly rejected.")

    # 7. Test Status Change (Deactivate / Activate)
    deactivate_res = client.patch(f"/api/v1/teachers/{teacher_id}/status", json={
        "status": "INACTIVE",
        "reason": "Sabbatical leave"
    }, headers=headers)
    assert deactivate_res.status_code == 200
    assert deactivate_res.json()["status"] == "INACTIVE"
    print(f"[OK] Teacher {teacher_id} soft-deactivated to INACTIVE.")

    activate_res = client.patch(f"/api/v1/teachers/{teacher_id}/status", json={
        "status": "ACTIVE",
        "reason": "Resumed duties"
    }, headers=headers)
    assert activate_res.status_code == 200
    assert activate_res.json()["status"] == "ACTIVE"
    print(f"[OK] Teacher {teacher_id} re-activated to ACTIVE.")

    # 8. Direct PostgreSQL DB Verification
    db = SessionLocal()
    try:
        db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
        assert db_teacher is not None
        assert db_teacher.first_name == "Mustaf"
        assert db_teacher.teacher_number == f"TCH-{rand_num}"
        assert db_teacher.user_id is not None

        db_assignments = db.query(TeacherAssignment).filter(TeacherAssignment.teacher_id == teacher_id).all()
        if class_id and subject_id:
            assert len(db_assignments) >= 1
            print(f"[OK] PostgreSQL verified {len(db_assignments)} assignment relationships.")

        print("[OK] Direct PostgreSQL query confirmed persistence and relational integrity.")
    finally:
        db.close()

    print("==================================================")
    print("ALL TEACHER REDESIGN INTEGRATION TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    test_teacher_management_features()
