import sys
import os
import random

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass

client = TestClient(app)

def test_student_management_features():
    print("==================================================")
    print("TESTING STUDENT MANAGEMENT REDESIGN & DATABASE INTEGRATION")
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

    # 2. Test Student Summary Metrics from PostgreSQL
    summary_res = client.get("/api/v1/students/summary", headers=headers)
    assert summary_res.status_code == 200, f"Summary failed: {summary_res.text}"
    summary = summary_res.json()
    print(f"[OK] Summary retrieved from PostgreSQL: {summary}")
    assert "total_students" in summary
    assert "active_students" in summary
    assert "inactive_students" in summary
    assert "unassigned_students" in summary
    assert summary["total_students"] >= 1

    # 3. Test Student Filtering (Search, Gender, Status, Class)
    # Search by 'Amina'
    search_res = client.get("/api/v1/students?query=Amina", headers=headers)
    assert search_res.status_code == 200
    search_items = search_res.json()
    print(f"[OK] Search 'Amina' returned {len(search_items)} students.")
    assert len(search_items) >= 1

    # Filter by Gender 'Male'
    male_res = client.get("/api/v1/students?gender=Male", headers=headers)
    assert male_res.status_code == 200
    male_items = male_res.json()
    print(f"[OK] Gender 'Male' filter returned {len(male_items)} students.")
    for item in male_items:
        assert item["gender"].lower() == "male"

    # 4. Test Student Creation with Portal & Class Assignment
    rand_num = random.randint(100000, 999999)
    # Fetch an existing class
    classes_res = client.get("/api/v1/classes", headers=headers)
    classes = classes_res.json()
    target_class = classes[0] if len(classes) > 0 else None
    class_id = target_class["id"] if target_class else None

    create_payload = {
        "first_name": "Khadija",
        "middle_name": "Ali",
        "last_name": "Warsame",
        "gender": "Female",
        "date_of_birth": "2010-05-15",
        "phone": "+252617778899",
        "address": "Wadajir District, Mogadishu",
        "admission_number": f"ADM-{rand_num}",
        "admission_date": "2026-09-01",
        "academic_year": "2026/2027",
        "initial_class_id": class_id,
        "status": "ACTIVE",
        "guardian_name": "Ali Warsame",
        "guardian_phone": "+252615554433",
        "guardian_relationship": "Father",
        "create_portal_account": True,
        "portal_username": f"khadija_{rand_num}",
        "portal_password": "Student@Hawlwadaag2026"
    }

    create_res = client.post("/api/v1/students", json=create_payload, headers=headers)
    assert create_res.status_code == 201, f"Student creation failed: {create_res.text}"
    created_student = create_res.json()
    student_id = created_student["id"]
    print(f"[OK] Created new student: {created_student['full_name']} (ID: {student_id}, Adm: {created_student['admission_number']})")
    assert created_student["has_portal_access"] is True

    # 5. Test Full Profile Retrieval
    profile_res = client.get(f"/api/v1/students/{student_id}/profile", headers=headers)
    assert profile_res.status_code == 200, f"Profile failed: {profile_res.text}"
    profile = profile_res.json()
    print(f"[OK] Full Profile retrieved: {profile['full_name']} | Class: {profile.get('current_class', {}).get('name') if profile.get('current_class') else 'None'} | Financials: {profile.get('financial_summary')}")
    assert profile["admission_number"] == f"ADM-{rand_num}"
    assert "financial_summary" in profile
    assert "fees" in profile
    assert "exam_results" in profile

    # 6. Test Status Change (Deactivate / Activate)
    deactivate_res = client.patch(f"/api/v1/students/{student_id}/status", json={
        "status": "INACTIVE",
        "reason": "Temporary transfer"
    }, headers=headers)
    assert deactivate_res.status_code == 200
    assert deactivate_res.json()["status"] == "INACTIVE"
    print(f"[OK] Student {student_id} soft-deactivated to INACTIVE.")

    activate_res = client.patch(f"/api/v1/students/{student_id}/status", json={
        "status": "ACTIVE",
        "reason": "Re-activated"
    }, headers=headers)
    assert activate_res.status_code == 200
    assert activate_res.json()["status"] == "ACTIVE"
    print(f"[OK] Student {student_id} re-activated to ACTIVE.")

    # 7. Direct PostgreSQL DB Verification
    db = SessionLocal()
    try:
        db_student = db.query(Student).filter(Student.id == student_id).first()
        assert db_student is not None
        assert db_student.first_name == "Khadija"
        assert db_student.admission_number == f"ADM-{rand_num}"
        assert db_student.user_id is not None

        db_enrollment = db.query(StudentEnrollment).filter(StudentEnrollment.student_id == student_id).first()
        if class_id:
            assert db_enrollment is not None
            assert db_enrollment.class_id == class_id
            print(f"[OK] PostgreSQL verified enrollment relationship for Class ID {class_id}.")

        print("[OK] Direct PostgreSQL query confirmed persistence and integrity.")
    finally:
        db.close()

    print("==================================================")
    print("ALL STUDENT REDESIGN INTEGRATION TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    test_student_management_features()
