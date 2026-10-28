import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.core.database import SessionLocal
from app.models.user import User
from app.models.teacher import Teacher
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.teacher_assignment import TeacherAssignment
from app.models.student_enrollment import StudentEnrollment


client = TestClient(app)


def get_teacher_token(username: str) -> str:
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if not user:
        raise ValueError(f"User {username} not found")
    return create_access_token(str(user.id))


def test_authenticated_teacher_loads_exact_assignments():
    """
    Requirement 1 & 20: Authenticated teacher loads assignments strictly from PostgreSQL
    using the authenticated session identity.
    """
    token = get_teacher_token("teacher.ahmed")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/teacher-portal/classes", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert isinstance(data, list)
    assert len(data) >= 3

    # Verify teacher identity
    for item in data:
        assert item["teacher_name"] == "Ahmed Hassan Ali"
        assert item["teacher_number"] == "TCH-001"
        assert item["status"] == "ACTIVE"


def test_actual_subject_name_and_code_displayed():
    """
    Requirement 2: Every assignment card clearly displays actual Subject Name and Subject Code.
    No empty subject codes or invented codes.
    """
    token = get_teacher_token("teacher.ahmed")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/teacher-portal/classes", headers=headers)
    assert res.status_code == 200
    data = res.json()

    # Ahmed teaches Mathematics (MATH-101) and Physics (PHY-201)
    subjects = {d["subject_name"]: d["subject_code"] for d in data}
    assert "Mathematics" in subjects
    assert subjects["Mathematics"] == "MATH-101"

    assert "Physics" in subjects
    assert subjects["Physics"] == "PHY-201"

    for item in data:
        assert item["subject_name"] is not None and len(item["subject_name"]) > 0
        assert item["subject_code"] is not None and len(item["subject_code"]) > 0
        assert item["class_name"] is not None and len(item["class_name"]) > 0
        assert item["academic_year"] is not None and len(item["academic_year"]) > 0
        assert item["student_count"] >= 0


def test_multiple_classes_and_subjects_distinct_identities():
    """
    Requirement 4, 5, 6:
    - Multiple classes for same subject retain individual assignment IDs.
    - Multiple subjects retain distinct assignment entries.
    - No duplicate assignments.
    """
    token = get_teacher_token("teacher.ahmed")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/teacher-portal/classes", headers=headers)
    assert res.status_code == 200
    data = res.json()

    ids = [d["id"] for d in data]
    assert len(ids) == len(set(ids)), "Assignment IDs must be unique (no duplicate cards)"

    math_classes = [d["class_name"] for d in data if d["subject_name"] == "Mathematics"]
    assert any("Grade 7" in c for c in math_classes)
    assert any("Grade 8" in c for c in math_classes)


def test_academic_year_filtering_and_status():
    """
    Requirement 7, 8, 12: Filters by academic year and marks assignments with status.
    """
    token = get_teacher_token("teacher.ahmed")
    headers = {"Authorization": f"Bearer {token}"}

    # Filter by 2025-2026 or 2025/2026
    res = client.get("/api/v1/teacher-portal/classes?academic_year=2025-2026", headers=headers)
    assert res.status_code == 200
    data = res.json()
    for item in data:
        assert item["academic_year"] in ["2025-2026", "2025/2026"]
        assert item["display_status"] in ["ACTIVE", "HISTORICAL", "INACTIVE"]


def test_security_idor_teacher_cannot_access_unassigned_class_detail():
    """
    Requirement 9, 14: Teacher A cannot access Teacher B's class details or student roster (403 Forbidden).
    """
    token_ahmed = get_teacher_token("teacher.ahmed")
    headers_ahmed = {"Authorization": f"Bearer {token_ahmed}"}

    # Grade 7 (class_id=31) is assigned to Ahmed -> 200 OK
    res_allowed = client.get("/api/v1/teacher-portal/classes/31/detail", headers=headers_ahmed)
    assert res_allowed.status_code == 200
    detail = res_allowed.json()
    assert "Grade 7" in detail["name"]
    assert len(detail["students"]) > 0

    # Class 34 (Form 2 - A) is assigned to Teacher Abdi, NOT Ahmed -> 403 Forbidden
    res_blocked = client.get("/api/v1/teacher-portal/classes/34/detail", headers=headers_ahmed)
    assert res_blocked.status_code == 403
    assert "not authorized" in res_blocked.json()["detail"].lower()


def test_unauthenticated_request_blocked():
    """
    Unauthenticated request to teacher classes endpoint must return 401 Unauthorized.
    """
    res = client.get("/api/v1/teacher-portal/classes")
    assert res.status_code in [401, 403]
