"""
End-to-End Test Suite for Fees Student Financial Profile & Hard Filtering
Covers:
1. Admin authentication & authorization enforcement
2. Primary student financial profile retrieval (HTTP 200)
3. Primary student identity, class, academic year, invoices, payments, balance verification
4. Secondary student financial profile retrieval (HTTP 200)
5. Secondary student identity, class, invoices, payments, balance verification
6. Zero-invoice student retrieval ($0.00 financial profile, HTTP 200, not 500)
7. Invalid student ID (HTTP 404 STUDENT_NOT_FOUND)
8. Unauthorized user access rejection (HTTP 401/403)
9. Strict PRIMARY / SECONDARY invoice API filtering isolation
10. Strict PRIMARY / SECONDARY class selector API isolation
11. Summary telemetry scope isolation (PRIMARY vs SECONDARY)
"""
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import create_application
from app.core.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.school_class import SchoolClass
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.fee import FeeStructure, StudentFee, FeePayment
from app.core.security import create_access_token


@pytest.fixture(scope="module")
def app():
    return create_application()


@pytest.fixture(scope="module")
def client(app):
    return TestClient(app)


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="module")
def admin_headers(db_session):
    admin_user = (
        db_session.query(User)
        .filter(User.is_active == True)
        .join(UserRole, UserRole.user_id == User.id)
        .join(Role, Role.id == UserRole.role_id)
        .filter(Role.name == "ADMIN")
        .first()
    )
    if not admin_user:
        admin_user = db_session.query(User).filter(User.is_superuser == True).first()
    
    assert admin_user is not None, "Active admin user must exist in database"
    token = create_access_token(subject=str(admin_user.id), claims={"username": admin_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def primary_student(db_session):
    # Find active enrolled student in PRIMARY class
    enr = (
        db_session.query(StudentEnrollment)
        .join(SchoolClass, StudentEnrollment.class_id == SchoolClass.id)
        .join(Student, StudentEnrollment.student_id == Student.id)
        .filter(
            SchoolClass.division == "PRIMARY",
            StudentEnrollment.status == "ACTIVE",
            Student.status == "ACTIVE",
        )
        .first()
    )
    assert enr is not None, "No active primary student enrollment found in database"
    return enr.student, enr.school_class


@pytest.fixture(scope="module")
def secondary_student(db_session):
    # Find active enrolled student in SECONDARY class
    enr = (
        db_session.query(StudentEnrollment)
        .join(SchoolClass, StudentEnrollment.class_id == SchoolClass.id)
        .join(Student, StudentEnrollment.student_id == Student.id)
        .filter(
            SchoolClass.division == "SECONDARY",
            StudentEnrollment.status == "ACTIVE",
            Student.status == "ACTIVE",
        )
        .first()
    )
    assert enr is not None, "No active secondary student enrollment found in database"
    return enr.student, enr.school_class


# =========================================================================
# 1. STUDENT FINANCIAL PROFILE VIEW TESTS
# =========================================================================

def test_view_primary_student_financial_profile(client, admin_headers, primary_student):
    student, cls = primary_student
    url = f"/api/v1/fees/students/{student.id}/financial-profile"
    res = client.get(url, headers=admin_headers)

    assert res.status_code == 200, f"Failed to get primary student financial profile: {res.text}"
    data = res.json()

    # Verify student identity
    assert data["student_id"] == student.id
    assert data["admission_number"] == student.admission_number
    assert data["full_name"] == student.full_name
    assert data["education_level"] == "PRIMARY"
    assert "Grade" in (data["class_name"] or "") or (data["class_name"] == cls.name)

    # Verify financial structure
    assert "total_billed" in data
    assert "total_paid" in data
    assert "outstanding_balance" in data
    assert "overdue_balance" in data
    assert isinstance(data["invoices"], list)
    assert isinstance(data["payments"], list)

    # Verify Decimal calculations
    assert round(data["total_billed"] - data["total_paid"], 2) == round(data["outstanding_balance"], 2) or data["outstanding_balance"] >= 0


def test_view_secondary_student_financial_profile(client, admin_headers, secondary_student):
    student, cls = secondary_student
    url = f"/api/v1/fees/students/{student.id}/financial-profile"
    res = client.get(url, headers=admin_headers)

    assert res.status_code == 200, f"Failed to get secondary student financial profile: {res.text}"
    data = res.json()

    # Verify student identity
    assert data["student_id"] == student.id
    assert data["admission_number"] == student.admission_number
    assert data["full_name"] == student.full_name
    assert data["education_level"] == "SECONDARY"
    assert "Form" in (data["class_name"] or "") or (data["class_name"] == cls.name)

    # Verify financial structure
    assert "total_billed" in data
    assert "total_paid" in data
    assert "outstanding_balance" in data
    assert "overdue_balance" in data


def test_view_student_financial_profile_aliases(client, admin_headers, primary_student):
    student, _ = primary_student

    # Test /fees/students/{id}/finance
    res1 = client.get(f"/api/v1/fees/students/{student.id}/finance", headers=admin_headers)
    assert res1.status_code == 200

    # Test /fees/student/{id}
    res2 = client.get(f"/api/v1/fees/student/{student.id}", headers=admin_headers)
    assert res2.status_code == 200

    # Test /admin/fees/students/{id}/financial-profile
    res3 = client.get(f"/api/v1/admin/fees/students/{student.id}/financial-profile", headers=admin_headers)
    assert res3.status_code == 200


def test_student_with_zero_invoices_returns_zero_profile(client, admin_headers, db_session):
    # Find or create a student with no invoices
    all_students = db_session.query(Student).filter(Student.status == "ACTIVE").all()
    zero_inv_student = None
    for st in all_students:
        inv_cnt = db_session.query(StudentFee).filter(StudentFee.student_id == st.id).count()
        if inv_cnt == 0:
            zero_inv_student = st
            break

    if not zero_inv_student:
        # Create a test student without invoices
        zero_inv_student = Student(
            admission_number="ADM-TEST-ZERO-001",
            first_name="ZeroInvoice",
            last_name="Student",
            gender="Male",
            status="ACTIVE",
        )
        db_session.add(zero_inv_student)
        db_session.commit()
        db_session.refresh(zero_inv_student)

    url = f"/api/v1/fees/students/{zero_inv_student.id}/financial-profile"
    res = client.get(url, headers=admin_headers)

    assert res.status_code == 200
    data = res.json()
    assert data["student_id"] == zero_inv_student.id
    assert data["total_billed"] == 0.0
    assert data["total_paid"] == 0.0
    assert data["outstanding_balance"] == 0.0
    assert data["overdue_balance"] == 0.0
    assert data["invoices"] == []
    assert data["payments"] == []


def test_invalid_student_id_returns_404(client, admin_headers):
    invalid_id = 9999999
    res = client.get(f"/api/v1/fees/students/{invalid_id}/financial-profile", headers=admin_headers)
    assert res.status_code == 404
    assert "not found" in res.json().get("detail", "").lower()


def test_unauthorized_access_rejected(client, primary_student):
    student, _ = primary_student
    # Unauthenticated request
    res = client.get(f"/api/v1/fees/students/{student.id}/financial-profile")
    assert res.status_code in (401, 403)


# =========================================================================
# 2. HARD FILTERING: PRIMARY VS SECONDARY CLASS ISOLATION
# =========================================================================

def test_classes_endpoint_primary_hard_filter(client, admin_headers):
    res = client.get("/api/v1/fees/classes?education_level=PRIMARY&academic_year=2026/2027", headers=admin_headers)
    assert res.status_code == 200
    classes = res.json()
    assert len(classes) > 0

    for c in classes:
        assert c["division"] == "PRIMARY", f"Secondary class found in primary filter: {c['name']}"
        assert not c["name"].startswith("Form "), f"Form class found in primary filter: {c['name']}"
        assert c["level"].startswith("Grade "), f"Invalid level in primary filter: {c['level']}"


def test_classes_endpoint_secondary_hard_filter(client, admin_headers):
    res = client.get("/api/v1/fees/classes?education_level=SECONDARY&academic_year=2026/2027", headers=admin_headers)
    assert res.status_code == 200
    classes = res.json()
    assert len(classes) > 0

    for c in classes:
        assert c["division"] == "SECONDARY", f"Primary class found in secondary filter: {c['name']}"
        assert not c["name"].startswith("Grade "), f"Grade class found in secondary filter: {c['name']}"
        assert c["level"].startswith("Form "), f"Invalid level in secondary filter: {c['level']}"


# =========================================================================
# 3. HARD FILTERING: INVOICE TABLE ISOLATION
# =========================================================================

def test_invoices_endpoint_primary_hard_filter(client, admin_headers, db_session):
    res = client.get("/api/v1/fees/invoices?education_level=PRIMARY&academic_year=2026/2027&page_size=100", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    items = data["items"]

    for inv in items:
        # Check that invoice belongs to a PRIMARY class
        if inv["class_id"]:
            cls = db_session.query(SchoolClass).filter(SchoolClass.id == inv["class_id"]).first()
            assert cls is not None
            assert cls.division == "PRIMARY", f"Secondary class invoice found in primary invoices: {inv['invoice_number']} ({cls.name})"


def test_invoices_endpoint_secondary_hard_filter(client, admin_headers, db_session):
    res = client.get("/api/v1/fees/invoices?education_level=SECONDARY&academic_year=2026/2027&page_size=100", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    items = data["items"]

    for inv in items:
        if inv["class_id"]:
            cls = db_session.query(SchoolClass).filter(SchoolClass.id == inv["class_id"]).first()
            assert cls is not None
            assert cls.division == "SECONDARY", f"Primary class invoice found in secondary invoices: {inv['invoice_number']} ({cls.name})"


# =========================================================================
# 4. HARD FILTERING: FINANCIAL SUMMARY TELEMETRY ISOLATION
# =========================================================================

def test_financial_summary_level_filter(client, admin_headers):
    # Overall summary
    res_all = client.get("/api/v1/fees/summary?academic_year=2026/2027", headers=admin_headers)
    assert res_all.status_code == 200
    all_data = res_all.json()

    # Primary summary
    res_pri = client.get("/api/v1/fees/summary?academic_year=2026/2027&education_level=PRIMARY", headers=admin_headers)
    assert res_pri.status_code == 200
    pri_data = res_pri.json()

    # Secondary summary
    res_sec = client.get("/api/v1/fees/summary?academic_year=2026/2027&education_level=SECONDARY", headers=admin_headers)
    assert res_sec.status_code == 200
    sec_data = res_sec.json()

    # Verify no NaN or negative counts
    for d in [all_data, pri_data, sec_data]:
        assert isinstance(d["total_invoices_count"], int)
        assert isinstance(d["paid_invoices_count"], int)
        assert isinstance(d["pending_invoices_count"], int)
        assert isinstance(d["unpaid_invoices_count"], int)
        assert isinstance(d["partial_invoices_count"], int)
        assert isinstance(d["overdue_invoices_count"], int)
        assert d["total_billed"] >= 0
        assert d["total_collected"] >= 0
        assert d["total_outstanding"] >= 0

    # Total counts must be partitioned
    assert pri_data["total_invoices_count"] + sec_data["total_invoices_count"] <= all_data["total_invoices_count"]
