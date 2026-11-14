import sys
import os
import random

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.subject import Subject

client = TestClient(app)

def test_class_management_features():
    print("==================================================")
    print("TESTING CLASS MANAGEMENT REDESIGN & DATABASE INTEGRATION")
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

    # 2. Test Class Summary Metrics from PostgreSQL
    summary_res = client.get("/api/v1/classes/summary", headers=headers)
    assert summary_res.status_code == 200, f"Summary failed: {summary_res.text}"
    summary = summary_res.json()
    print(f"[OK] Summary retrieved from PostgreSQL: {summary}")
    assert "total_classes" in summary
    assert "active_classes" in summary
    assert "total_students_enrolled" in summary
    assert "available_seats" in summary
    assert "near_capacity_classes" in summary
    assert summary["total_classes"] >= 1

    # 3. Test Class Filtering and Search
    search_res = client.get("/api/v1/classes?query=Grade", headers=headers)
    assert search_res.status_code == 200
    search_items = search_res.json()
    print(f"[OK] Search 'Grade' returned {len(search_items)} classes.")
    assert len(search_items) >= 1

    # Filter by Status 'ACTIVE'
    active_res = client.get("/api/v1/classes?status=ACTIVE", headers=headers)
    assert active_res.status_code == 200
    active_items = active_res.json()
    print(f"[OK] Status 'ACTIVE' filter returned {len(active_items)} classes.")
    for item in active_items:
        assert item["status"].upper() == "ACTIVE"

    # 4. Test Class Creation with Unique Code and Duplicate Combo Prevention
    rand_num = random.randint(100000, 999999)
    class_code = f"CLS-{rand_num}"
    create_payload = {
        "name": f"Grade 10 Delta {rand_num}",
        "code": class_code,
        "section": "Delta Stream",
        "academic_year": "2026/2027",
        "capacity": 35,
        "description": "Secondary school Grade 10 Delta stream",
        "status": "ACTIVE"
    }

    create_res = client.post("/api/v1/classes", json=create_payload, headers=headers)
    assert create_res.status_code == 201, f"Class creation failed: {create_res.text}"
    created_class = create_res.json()
    class_id = created_class["id"]
    print(f"[OK] Created new class: {created_class['name']} (ID: {class_id}, Code: {created_class['code']})")

    # Duplicate code rejection check
    dup_code_res = client.post("/api/v1/classes", json={
        "name": "Different Class Name",
        "code": class_code,
        "academic_year": "2026/2027",
        "capacity": 30
    }, headers=headers)
    assert dup_code_res.status_code == 409, f"Duplicate code was not rejected: {dup_code_res.status_code}"
    print("[OK] Duplicate class code properly rejected with 409 Conflict.")

    # Duplicate name + section + academic year rejection check
    dup_combo_res = client.post("/api/v1/classes", json={
        "name": f"Grade 10 Delta {rand_num}",
        "code": f"DIFF-{rand_num}",
        "section": "Delta Stream",
        "academic_year": "2026/2027",
        "capacity": 30
    }, headers=headers)
    assert dup_combo_res.status_code == 409, f"Duplicate name/section/year was not rejected: {dup_combo_res.status_code}"
    print("[OK] Duplicate class identity (name + section + year) properly rejected with 409 Conflict.")

    # 5. Test Full Class Profile Retrieval
    profile_res = client.get(f"/api/v1/classes/{class_id}/full", headers=headers)
    assert profile_res.status_code == 200, f"Full Profile failed: {profile_res.text}"
    profile = profile_res.json()
    print(f"[OK] Full Profile retrieved: {profile['name']} | Capacity: {profile['capacity_metrics']}")
    assert profile["code"] == class_code
    assert "capacity_metrics" in profile
    assert "students" in profile
    assert "teachers" in profile
    assert "subjects" in profile
    assert "timetables" in profile
    assert "exams" in profile

    # 6. Test Student Enrollment & Duplicate Prevention
    # Fetch an existing student
    students_res = client.get("/api/v1/students", headers=headers)
    students = students_res.json()
    assert len(students) > 0, "No students found in DB."
    target_student = students[0]
    student_id = target_student["id"]

    enroll_payload = {
        "student_id": student_id,
        "academic_year": "2026/2027"
    }
    enroll_res = client.post(f"/api/v1/classes/{class_id}/students", json=enroll_payload, headers=headers)
    # If student is already enrolled in another class for 2026/2027, it should reject with 409
    if enroll_res.status_code == 409:
        print(f"[OK] Student {student_id} already enrolled in another class; duplicate enrollment properly prevented.")
    else:
        assert enroll_res.status_code == 201, f"Enrollment failed: {enroll_res.text}"
        print(f"[OK] Student {student_id} enrolled in Class {class_id}.")

    # 7. Test Teacher Assignment & Duplicate Prevention
    teachers_res = client.get("/api/v1/teachers", headers=headers)
    teachers = teachers_res.json()
    assert len(teachers) > 0, "No teachers found in DB."
    teacher_id = teachers[0]["id"]

    subjects_res = client.get("/api/v1/subjects", headers=headers)
    subjects = subjects_res.json()
    assert len(subjects) > 0, "No subjects found in DB."
    subject_id = subjects[0]["id"]

    assign_payload = {
        "teacher_id": teacher_id,
        "subject_id": subject_id,
        "academic_year": "2026/2027"
    }
    assign_res = client.post(f"/api/v1/classes/{class_id}/teachers", json=assign_payload, headers=headers)
    assert assign_res.status_code == 201, f"Teacher assignment failed: {assign_res.text}"
    assignment_id = assign_res.json()["assignment_id"]
    print(f"[OK] Teacher {teacher_id} assigned to Class {class_id} for Subject {subject_id}.")

    # Duplicate teacher assignment rejection
    dup_assign_res = client.post(f"/api/v1/classes/{class_id}/teachers", json=assign_payload, headers=headers)
    assert dup_assign_res.status_code == 409, f"Duplicate teacher assignment not rejected: {dup_assign_res.status_code}"
    print("[OK] Duplicate teacher assignment properly rejected with 409 Conflict.")

    # 8. Test Status Change (Deactivate / Activate / Archive)
    deactivate_res = client.patch(f"/api/v1/classes/{class_id}/status", json={
        "status": "INACTIVE",
        "reason": "End of academic term"
    }, headers=headers)
    assert deactivate_res.status_code == 200
    assert deactivate_res.json()["status"] == "INACTIVE"
    print(f"[OK] Class {class_id} soft-deactivated to INACTIVE.")

    activate_res = client.patch(f"/api/v1/classes/{class_id}/status", json={
        "status": "ACTIVE",
        "reason": "Re-opened for new term"
    }, headers=headers)
    assert activate_res.status_code == 200
    assert activate_res.json()["status"] == "ACTIVE"
    print(f"[OK] Class {class_id} re-activated to ACTIVE.")

    # 9. Direct PostgreSQL DB Verification
    db = SessionLocal()
    try:
        db_class = db.query(SchoolClass).filter(SchoolClass.id == class_id).first()
        assert db_class is not None
        assert db_class.code == class_code
        assert db_class.capacity == 35

        db_assignments = db.query(TeacherAssignment).filter(
            TeacherAssignment.class_id == class_id,
            TeacherAssignment.status == "ACTIVE"
        ).all()
        assert len(db_assignments) >= 1
        print(f"[OK] PostgreSQL verified {len(db_assignments)} teacher assignment relationship.")

        print("[OK] Direct PostgreSQL query confirmed persistence and relational integrity.")
    finally:
        db.close()

    print("==================================================")
    print("ALL CLASS REDESIGN INTEGRATION TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    test_class_management_features()
