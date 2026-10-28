import sys
import os
import random

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.subject import Subject
from app.models.school_class import SchoolClass
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment

client = TestClient(app)

def test_subject_management_features():
    print("==================================================")
    print("TESTING SUBJECT MANAGEMENT REDESIGN & DATABASE INTEGRATION")
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

    # 2. Test Subject Summary Metrics from PostgreSQL
    summary_res = client.get("/api/v1/subjects/summary", headers=headers)
    assert summary_res.status_code == 200, f"Summary failed: {summary_res.text}"
    summary = summary_res.json()
    print(f"[OK] Summary retrieved from PostgreSQL: {summary}")
    assert "total_subjects" in summary
    assert "active_subjects" in summary
    assert "assigned_subjects" in summary
    assert "unassigned_subjects" in summary
    assert "departments_count" in summary
    assert summary["total_subjects"] >= 1

    # 3. Test Departments list endpoint
    dept_res = client.get("/api/v1/subjects/departments", headers=headers)
    assert dept_res.status_code == 200
    depts = dept_res.json()
    print(f"[OK] Distinct departments retrieved: {depts}")
    assert isinstance(depts, list)

    # 4. Test Subject Filtering and Search
    search_res = client.get("/api/v1/subjects?query=Mathematics", headers=headers)
    assert search_res.status_code == 200
    search_items = search_res.json()
    print(f"[OK] Search 'Mathematics' returned {len(search_items)} subjects.")
    assert len(search_items) >= 1

    # Filter by Status 'ACTIVE'
    active_res = client.get("/api/v1/subjects?status=ACTIVE", headers=headers)
    assert active_res.status_code == 200
    active_items = active_res.json()
    print(f"[OK] Status 'ACTIVE' filter returned {len(active_items)} subjects.")
    for item in active_items:
        assert item["status"].upper() == "ACTIVE"

    # 5. Test Subject Creation with Unique Code and Duplicate Code Prevention
    rand_num = random.randint(100000, 999999)
    sub_code = f"SUB-{rand_num}"
    create_payload = {
        "name": f"Advanced Astronomy {rand_num}",
        "code": sub_code,
        "department": "Sciences",
        "description": "Exploration of astrophysics, observational astronomy and cosmological mechanics.",
        "status": "ACTIVE"
    }

    create_res = client.post("/api/v1/subjects", json=create_payload, headers=headers)
    assert create_res.status_code == 201, f"Subject creation failed: {create_res.text}"
    created_sub = create_res.json()
    subject_id = created_sub["id"]
    print(f"[OK] Created new subject: {created_sub['name']} (ID: {subject_id}, Code: {created_sub['code']})")

    # Duplicate code rejection check
    dup_res = client.post("/api/v1/subjects", json={
        "name": "Different Subject Name",
        "code": sub_code,
        "department": "Sciences",
        "status": "ACTIVE"
    }, headers=headers)
    assert dup_res.status_code == 409, f"Duplicate subject code was not rejected: {dup_res.status_code}"
    print("[OK] Duplicate subject code properly rejected with 409 Conflict.")

    # 6. Test Full Subject Profile Retrieval
    profile_res = client.get(f"/api/v1/subjects/{subject_id}/full", headers=headers)
    assert profile_res.status_code == 200, f"Full Profile failed: {profile_res.text}"
    profile = profile_res.json()
    print(f"[OK] Full Profile retrieved: {profile['name']} | Code: {profile['code']} | Dept: {profile['department']}")
    assert profile["code"] == sub_code
    assert "classes" in profile
    assert "teachers" in profile
    assert "timetables" in profile
    assert "exams" in profile

    # 7. Test Subject Assignment to Class and Duplicate Prevention
    classes_res = client.get("/api/v1/classes", headers=headers)
    classes = classes_res.json()
    assert len(classes) > 0, "No classes found."
    target_class = classes[0]
    class_id = target_class["id"]

    teachers_res = client.get("/api/v1/teachers", headers=headers)
    teachers = teachers_res.json()
    assert len(teachers) > 0, "No teachers found."
    target_teacher = teachers[0]
    teacher_id = target_teacher["id"]

    assign_payload = {
        "class_id": class_id,
        "academic_year": "2025-2026",
        "teacher_id": teacher_id
    }
    assign_res = client.post(f"/api/v1/subjects/{subject_id}/classes", json=assign_payload, headers=headers)
    assert assign_res.status_code == 201, f"Subject class assignment failed: {assign_res.text}"
    assignment_id = assign_res.json()["assignment_id"]
    print(f"[OK] Subject {subject_id} assigned to Class {class_id} with Teacher {teacher_id}.")

    # Duplicate assignment rejection
    dup_assign_res = client.post(f"/api/v1/subjects/{subject_id}/classes", json=assign_payload, headers=headers)
    assert dup_assign_res.status_code == 409, f"Duplicate assignment was not rejected: {dup_assign_res.status_code}"
    print("[OK] Duplicate subject-class-teacher assignment properly rejected with 409 Conflict.")

    # 8. Test Status Change (Deactivate / Activate)
    deactivate_res = client.patch(f"/api/v1/subjects/{subject_id}/status", json={
        "status": "INACTIVE",
        "reason": "Elective term expired"
    }, headers=headers)
    assert deactivate_res.status_code == 200
    assert deactivate_res.json()["status"] == "INACTIVE"
    print(f"[OK] Subject {subject_id} soft-deactivated to INACTIVE.")

    activate_res = client.patch(f"/api/v1/subjects/{subject_id}/status", json={
        "status": "ACTIVE",
        "reason": "Re-instated curriculum"
    }, headers=headers)
    assert activate_res.status_code == 200
    assert activate_res.json()["status"] == "ACTIVE"
    print(f"[OK] Subject {subject_id} re-activated to ACTIVE.")

    # 9. Direct PostgreSQL DB Verification
    db = SessionLocal()
    try:
        db_sub = db.query(Subject).filter(Subject.id == subject_id).first()
        assert db_sub is not None
        assert db_sub.code == sub_code
        assert db_sub.department == "Sciences"

        db_assignments = db.query(TeacherAssignment).filter(
            TeacherAssignment.subject_id == subject_id,
            TeacherAssignment.status == "ACTIVE"
        ).all()
        assert len(db_assignments) >= 1
        print(f"[OK] PostgreSQL verified {len(db_assignments)} active teacher-subject assignments.")

        print("[OK] Direct PostgreSQL query confirmed persistence and relational integrity.")
    finally:
        db.close()

    print("==================================================")
    print("ALL SUBJECT REDESIGN INTEGRATION TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    test_subject_management_features()
