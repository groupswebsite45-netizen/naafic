import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.user import User
from app.core.security import get_password_hash, create_access_token


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def admin_token(db_session):
    admin = db_session.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@hawlwadaagschool.edu.so",
            hashed_password=get_password_hash("Admin@Hawlwadaag2026"),
            full_name="System Administrator",
            is_active=True,
            is_superuser=True
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
    return create_access_token(subject=str(admin.id), claims={"username": admin.username})


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


class TestClassesAndSubjectsArchitecture:
    """
    Comprehensive test suite enforcing Hawlwadaag Primary and Secondary School's
    academic architecture:
    - Primary (Grades 1-8) & Secondary (Forms 1-4) structure
    - Dynamic section management (A, B, C, D, E, F...)
    - Duplicate class prevention (HTTP 409)
    - Student duplicate active enrollment prevention (HTTP 409)
    - Subject division isolation (Primary vs Secondary)
    - Teacher assignment curriculum validation
    - Class-specific subject filtering
    """

    def test_01_create_primary_class_success(self, client: TestClient, auth_headers):
        """Test creating a valid Primary class (Grade 7 - Section C)."""
        payload = {
            "division": "PRIMARY",
            "level": "Grade 7",
            "section": "C",
            "academic_year": "2026/2027",
            "capacity": 45,
            "description": "Grade 7 Stream C",
            "status": "ACTIVE"
        }
        res = client.post("/api/v1/classes", json=payload, headers=auth_headers)
        assert res.status_code in [201, 409]
        if res.status_code == 201:
            data = res.json()
            assert data["division"] == "PRIMARY"
            assert data["level"] == "Grade 7"
            assert data["section"] == "C"
            assert data["name"] == "Grade 7 - C"

    def test_02_create_secondary_class_success(self, client: TestClient, auth_headers):
        """Test creating a valid Secondary class (Form 1 - Section B)."""
        payload = {
            "division": "SECONDARY",
            "level": "Form 1",
            "section": "B",
            "academic_year": "2026/2027",
            "capacity": 40,
            "description": "Form 1 Stream B",
            "status": "ACTIVE"
        }
        res = client.post("/api/v1/classes", json=payload, headers=auth_headers)
        assert res.status_code in [201, 409]
        if res.status_code == 201:
            data = res.json()
            assert data["division"] == "SECONDARY"
            assert data["level"] == "Form 1"
            assert data["section"] == "B"
            assert data["name"] == "Form 1 - B"

    def test_03_invalid_division_level_combination_rejected(self, client: TestClient, auth_headers):
        """Primary division with Form 1 or Secondary division with Grade 7 must be rejected (422)."""
        # Primary with Form 2 -> REJECT
        res1 = client.post("/api/v1/classes", json={
            "division": "PRIMARY",
            "level": "Form 2",
            "section": "A",
            "academic_year": "2026/2027",
            "capacity": 40
        }, headers=auth_headers)
        assert res1.status_code == 422

        # Secondary with Grade 5 -> REJECT
        res2 = client.post("/api/v1/classes", json={
            "division": "SECONDARY",
            "level": "Grade 5",
            "section": "A",
            "academic_year": "2026/2027",
            "capacity": 40
        }, headers=auth_headers)
        assert res2.status_code == 422

    def test_04_duplicate_class_creation_prevented(self, client: TestClient, auth_headers):
        """Creating an identical class for the same academic year must be rejected with 409 Conflict."""
        payload = {
            "division": "PRIMARY",
            "level": "Grade 7",
            "section": "A",
            "academic_year": "2026/2027",
            "capacity": 40
        }
        # First attempt (might already exist from seed)
        res1 = client.post("/api/v1/classes", json=payload, headers=auth_headers)
        # Second attempt MUST be 409 Conflict
        res2 = client.post("/api/v1/classes", json=payload, headers=auth_headers)
        assert res2.status_code == 409
        assert "already exists" in res2.json()["detail"].lower()

    def test_05_dynamic_section_support(self, client: TestClient, auth_headers, db_session):
        """System supports dynamic sections such as E, F, Stream North."""
        payload = {
            "division": "PRIMARY",
            "level": "Grade 4",
            "section": "E",
            "academic_year": "2026/2027",
            "capacity": 35
        }
        res = client.post("/api/v1/classes", json=payload, headers=auth_headers)
        assert res.status_code in [201, 409]
        if res.status_code == 201:
            data = res.json()
            assert data["section"] == "E"
            assert data["name"] == "Grade 4 - E"

    def test_06_filter_classes_by_division(self, client: TestClient, auth_headers):
        """Filtering by division=PRIMARY returns only Primary classes; division=SECONDARY returns only Secondary."""
        # Primary filter
        res_prim = client.get("/api/v1/classes?division=PRIMARY", headers=auth_headers)
        assert res_prim.status_code == 200
        prim_classes = res_prim.json()
        assert len(prim_classes) > 0
        for c in prim_classes:
            assert c["division"] == "PRIMARY"
            assert ("Grade" in (c.get("level") or "") or "Grade" in c["name"] or "G" in c["code"])

        # Secondary filter
        res_sec = client.get("/api/v1/classes?division=SECONDARY", headers=auth_headers)
        assert res_sec.status_code == 200
        sec_classes = res_sec.json()
        assert len(sec_classes) > 0
        for c in sec_classes:
            assert c["division"] == "SECONDARY"
            assert ("Form" in (c.get("level") or "") or "Form" in c["name"] or "F" in c["code"])

    def test_07_subject_isolation_in_subject_listing(self, client: TestClient, auth_headers):
        """Subjects must be isolatable by division (PRIMARY vs SECONDARY)."""
        # Primary subjects
        res_prim = client.get("/api/v1/subjects?division=PRIMARY", headers=auth_headers)
        assert res_prim.status_code == 200
        prim_subs = res_prim.json()
        prim_names = [s["name"] for s in prim_subs]
        # Physics and Chemistry are secondary only and should not appear
        assert "Physics" not in prim_names
        assert "Chemistry" not in prim_names
        assert "Biology" not in prim_names

        # Secondary subjects
        res_sec = client.get("/api/v1/subjects?division=SECONDARY", headers=auth_headers)
        assert res_sec.status_code == 200
        sec_subs = res_sec.json()
        sec_names = [s["name"] for s in sec_subs]
        assert "Physics" in sec_names or "Chemistry" in sec_names

    def test_08_cross_division_subject_assignment_rejected(self, client: TestClient, auth_headers, db_session):
        """Assigning a Secondary-only subject (e.g. Physics) to a Primary class (e.g. Grade 2) must be rejected (422)."""
        # Find Physics (Secondary)
        physics = db_session.query(Subject).filter(Subject.name.ilike("Physics")).first()
        # Find Grade 2 - A (Primary)
        grade2 = db_session.query(SchoolClass).filter(
            SchoolClass.level == "Grade 2",
            SchoolClass.division == "PRIMARY"
        ).first()

        if physics and grade2:
            res = client.post(f"/api/v1/subjects/{physics.id}/classes", json={
                "class_id": grade2.id,
                "academic_year": grade2.academic_year
            }, headers=auth_headers)
            assert res.status_code == 422
            assert "cannot be assigned" in res.json()["detail"].lower()

    def test_09_student_duplicate_enrollment_prevention(self, client: TestClient, auth_headers, db_session):
        """A student cannot have two active enrollments in the same academic year (409 Conflict)."""
        # Find an active student
        student = db_session.query(Student).filter(Student.status == "ACTIVE").first()
        # Find two different classes in 2026/2027
        classes = db_session.query(SchoolClass).filter(
            SchoolClass.academic_year.in_(["2026/2027", "2026-2027"]),
            SchoolClass.status == "ACTIVE"
        ).limit(2).all()

        if student and len(classes) >= 2:
            c1, c2 = classes[0], classes[1]
            # Ensure student is enrolled in c1 first
            enroll_res = client.post(f"/api/v1/classes/{c1.id}/students", json={
                "student_id": student.id,
                "academic_year": c1.academic_year
            }, headers=auth_headers)
            assert enroll_res.status_code in [201, 409]

            # Attempting to enroll in c1 again -> 409 Conflict
            res_same = client.post(f"/api/v1/classes/{c1.id}/students", json={
                "student_id": student.id,
                "academic_year": c1.academic_year
            }, headers=auth_headers)
            assert res_same.status_code == 409
            assert "already" in res_same.json()["detail"].lower()

            # Attempting to enroll in c2 for same year -> 409 Conflict
            res_other = client.post(f"/api/v1/classes/{c2.id}/students", json={
                "student_id": student.id,
                "academic_year": c1.academic_year
            }, headers=auth_headers)
            assert res_other.status_code == 409
            assert "already enrolled" in res_other.json()["detail"].lower()
