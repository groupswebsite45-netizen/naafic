"""Comprehensive End-to-End and Security Test Suite for Student Portal."""
import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.database import SessionLocal
from app.models.student_result_view import StudentResultView

client = TestClient(app)


def get_token(username, password="Student@Hawlwadaag2026"):
    res = client.post("/api/v1/auth/login", json={"identifier": username, "password": password})
    assert res.status_code == 200, f"Login failed for {username}: {res.text}"
    return res.json()["access_token"]


def test_unauthenticated_requests_blocked():
    """Unauthenticated requests must be rejected with 401."""
    endpoints = [
        "/api/v1/student-portal/dashboard",
        "/api/v1/student-portal/profile",
        "/api/v1/student-portal/class",
        "/api/v1/student-portal/timetable",
        "/api/v1/student-portal/attendance",
        "/api/v1/student-portal/fees",
        "/api/v1/student-portal/exams",
    ]
    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 401, f"Expected 401 for unauthenticated {ep}, got {res.status_code}"


def test_admin_blocked_from_student_portal():
    """Admin role must not be permitted on student-only endpoints (403)."""
    admin_token = get_token("admin", "Admin@Hawlwadaag2026")
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/v1/student-portal/dashboard", headers=headers)
    assert res.status_code == 403, f"Admin should receive 403 on student portal, got {res.status_code}"


def test_student_dashboard_real_data():
    """Student 1 dashboard must contain accurate real data from PostgreSQL."""
    token = get_token("student.mustaf")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/student-portal/dashboard", headers=headers)
    assert res.status_code == 200
    data = res.json()

    # Verify student profile
    assert data["student"]["admission_number"] == "ADM-2026-001"
    assert "Mustaf" in data["student"]["full_name"]
    assert data["current_class"]["code"] == "G7-A"

    # Verify attendance summary from PostgreSQL
    assert data["attendance_summary"] is not None
    assert data["attendance_summary"]["total_classes"] == 45
    assert data["attendance_summary"]["present_count"] == 42
    assert data["attendance_summary"]["absent_count"] == 3
    assert data["attendance_summary"]["attendance_percentage"] == 93.3

    # Verify timetable
    assert data["enrolled_subjects_count"] > 0


def test_student_profile_read_only():
    """Student profile must be viewable but strictly read-only."""
    token = get_token("student.mustaf")
    headers = {"Authorization": f"Bearer {token}"}

    # GET profile
    res = client.get("/api/v1/student-portal/profile", headers=headers)
    assert res.status_code == 200
    profile = res.json()
    assert profile["admission_number"] == "ADM-2026-001"
    assert profile["guardian_name"] == "Ali Yusuf"

    # Attempt PUT/POST/PATCH - must be rejected by HTTP 405
    put_res = client.put("/api/v1/student-portal/profile", json={"first_name": "Hacker"}, headers=headers)
    assert put_res.status_code == 405

    post_res = client.post("/api/v1/student-portal/profile", json={"first_name": "Hacker"}, headers=headers)
    assert post_res.status_code == 405


def test_student_class_and_history():
    """Student class details must show enrolled subjects, teachers, and enrollment history."""
    token = get_token("student.mustaf")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/student-portal/class", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["school_class"]["code"] == "G7-A"
    assert len(data["subjects"]) > 0
    # Every subject must have name, code, status
    for s in data["subjects"]:
        assert s["name"]
        assert s["code"]
        assert s["status"] == "ACTIVE"

    # Enrollment history must include current academic year
    assert len(data["enrollment_history"]) >= 1
    enr_years = [e["academic_year"] for e in data["enrollment_history"]]
    assert "2025-2026" in enr_years


def test_student_timetable():
    """Student timetable must return weekly schedule periods for enrolled class."""
    token = get_token("student.mustaf")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/student-portal/timetable", headers=headers)
    assert res.status_code == 200
    slots = res.json()
    assert len(slots) > 0
    # Every slot must contain subject and day
    days = [s["day_of_week"] for s in slots]
    assert "Monday" in days


def test_student_attendance_isolation_and_filters():
    """
    Test attendance isolation:
    Student 1 (Mustaf): 42 present, 3 absent, Math 10 present 1 absent
    Student 2 (Amina): 44 present, 1 absent, Science 1 absent
    Student 1 must NEVER see Student 2 records.
    """
    s1_token = get_token("student.mustaf")
    s2_token = get_token("student.amina")

    # Student 1 query
    r1 = client.get("/api/v1/student-portal/attendance", headers={"Authorization": f"Bearer {s1_token}"})
    assert r1.status_code == 200
    s1_att = r1.json()
    assert s1_att["summary"]["present_count"] == 42
    assert s1_att["summary"]["absent_count"] == 3

    # Student 2 query
    r2 = client.get("/api/v1/student-portal/attendance", headers={"Authorization": f"Bearer {s2_token}"})
    assert r2.status_code == 200
    s2_att = r2.json()
    assert s2_att["summary"]["present_count"] == 44
    assert s2_att["summary"]["absent_count"] == 1

    # Student 1 filter by status=ABSENT
    r_filter = client.get("/api/v1/student-portal/attendance?status=ABSENT", headers={"Authorization": f"Bearer {s1_token}"})
    assert r_filter.status_code == 200
    absent_records = r_filter.json()["history"]
    assert len(absent_records) == 3
    for rec in absent_records:
        assert rec["status"] == "ABSENT"


def test_student_fees_isolation():
    """
    Verify fee isolation:
    Student 1 and Student 2 see strictly their own invoices.
    """
    s1_token = get_token("student.mustaf")
    s2_token = get_token("student.amina")

    r1 = client.get("/api/v1/student-portal/fees", headers={"Authorization": f"Bearer {s1_token}"})
    assert r1.status_code == 200
    f1 = r1.json()
    assert len(f1["fees"]) > 0
    assert f1["summary"]["total_billed"] > 0
    # Mustaf has PARTIALLY_PAID status
    assert any(inv["status"] == "PARTIALLY_PAID" for inv in f1["fees"])

    r2 = client.get("/api/v1/student-portal/fees", headers={"Authorization": f"Bearer {s2_token}"})
    assert r2.status_code == 200
    f2 = r2.json()
    # Amina has PENDING status
    assert any(inv["status"] == "PENDING" for inv in f2["fees"])


def test_student_exams_visibility_gate():
    """
    CRITICAL RESULT VISIBILITY GATE:
    Student 1 has DRAFT (result 1, 5, 9), APPROVED (result 45, 52), and RELEASED (result 61).
    Student 1 must ONLY see results with status == 'RELEASED'!
    """
    token = get_token("student.mustaf")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/student-portal/exams", headers=headers)
    assert res.status_code == 200
    results = res.json()

    for r in results:
        assert r["status"] == "RELEASED", f"Unreleased result exposed! status={r['status']}"

    # Verify view tracking
    if results:
        sample = results[0]
        view_res = client.post(
            "/api/v1/student-portal/exams/record-view",
            json={
                "exam_name": sample["exam_name"],
                "academic_year": sample["academic_year"],
                "class_id": sample["class_id"],
            },
            headers=headers
        )
        assert view_res.status_code == 200
        view_data = view_res.json()
        assert view_data["success"] is True
        assert view_data["view_count"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
