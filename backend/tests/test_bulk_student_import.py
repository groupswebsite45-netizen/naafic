import io
import uuid
import openpyxl
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.user import User
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass
from app.models.fee import FeeStructure, StudentFee
from app.services.fee_service import FeeService


def create_test_excel_bytes(rows_data, include_headers=True):
    """Helper to generate in-memory Excel workbook bytes."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Students_Import"

    if include_headers:
        headers = [
            "First Name *",
            "Middle Name",
            "Last Name *",
            "Gender *",
            "Date of Birth (YYYY-MM-DD)",
            "Guardian Name *",
            "Guardian Phone *",
            "Guardian Email",
            "Guardian Relationship",
            "Student Phone",
            "Residential Address",
            "Admission # (Optional)",
        ]
        ws.append(headers)

    for row in rows_data:
        ws.append(row)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="module")
def admin_headers(db_session: Session):
    admin_user = db_session.query(User).filter(User.username == "admin").first()
    token = create_access_token(subject=str(admin_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def teacher_headers(db_session: Session):
    teacher_user = db_session.query(User).filter(User.username == "teacher.fadumo").first()
    token = create_access_token(subject=str(teacher_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def student_headers(db_session: Session):
    student_user = db_session.query(User).filter(User.username == "student.khaalid").first()
    token = create_access_token(subject=str(student_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def primary_class(db_session: Session):
    """Retrieve canonical primary class for import testing."""
    c = db_session.query(SchoolClass).filter(
        SchoolClass.id == 32
    ).first()
    if not c:
        c = db_session.query(SchoolClass).filter(
            SchoolClass.division == "PRIMARY",
            SchoolClass.academic_year == "2026/2027",
            SchoolClass.status == "ACTIVE",
        ).first()
    return c


@pytest.fixture(scope="module")
def secondary_class(db_session: Session):
    """Retrieve canonical secondary class for import testing."""
    c = db_session.query(SchoolClass).filter(
        SchoolClass.id == 157
    ).first()
    if not c:
        c = db_session.query(SchoolClass).filter(
            SchoolClass.division == "SECONDARY",
            SchoolClass.academic_year == "2026/2027",
            SchoolClass.status == "ACTIVE",
        ).first()
    return c


# =============================================================================
# 1. DOWNLOAD TEMPLATE TEST
# =============================================================================

def test_download_template(client, admin_headers):
    """Test downloading the standard student Excel template."""
    res = client.get("/api/v1/students/import/template", headers=admin_headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(res.content) > 1000

    # Parse downloaded template
    wb = openpyxl.load_workbook(io.BytesIO(res.content))
    ws = wb.active
    assert ws.title == "Students_Import"
    assert ws.cell(row=1, column=1).value == "First Name *"
    assert ws.cell(row=1, column=4).value == "Gender * (Male/Female)"
    assert ws.cell(row=1, column=6).value == "Guardian Name *"


# =============================================================================
# 2. VALIDATION & PREVIEW OF 10 VALID STUDENTS
# =============================================================================

def test_preview_valid_students(client, admin_headers, primary_class):
    """Upload valid 10 students and verify preview matches."""
    tag = uuid.uuid4().hex[:5].upper()
    sample_students = [
        (f"Khadar{i}", "Ali", f"Warsame{tag}", "Male", "2012-01-10", "Ali Warsame", f"+25261518{i:04d}", "", "Father", "", "Mogadishu", f"ADM-PREV-{tag}-{i:03d}")
        for i in range(1, 11)
    ]
    excel_bytes = create_test_excel_bytes(sample_students)

    files = {"file": ("students_valid_10.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"class_id": primary_class.id, "academic_year": "2026/2027"}

    res = client.post("/api/v1/students/import/preview", headers=admin_headers, files=files, data=data)
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["total_rows"] == 10
    assert json_data["valid_rows"] == 10
    assert json_data["error_rows"] == 0
    assert len(json_data["rows"]) == 10


# =============================================================================
# 3. IMPORT EXECUTION & POSTGRESQL ENROLLMENT VERIFICATION
# =============================================================================

def test_execute_import_creates_students_and_enrollments(client, admin_headers, primary_class, db_session):
    """Execute import of 10 students into Primary Class and verify PostgreSQL records."""
    tag = uuid.uuid4().hex[:5].upper()
    sample_students = [
        (f"Khadar{i}", "Ali", f"Warsame{tag}", "Male", "2012-01-10", "Ali Warsame", f"+25261519{i:04d}", "", "Father", "", "Mogadishu", f"ADM-IMP-{tag}-{i:03d}")
        for i in range(1, 11)
    ]
    excel_bytes = create_test_excel_bytes(sample_students)

    # Preview first
    files = {"file": (f"students_import_{tag}.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"class_id": primary_class.id, "academic_year": "2026/2027"}
    prev_res = client.post("/api/v1/students/import/preview", headers=admin_headers, files=files, data=data)
    assert prev_res.status_code == 200
    rows = prev_res.json()["rows"]

    # Execute
    exec_payload = {
        "class_id": primary_class.id,
        "academic_year": "2026/2027",
        "file_name": f"students_import_{tag}.xlsx",
        "rows": rows,
        "enroll_existing_students": False,
    }
    exec_res = client.post("/api/v1/students/import/execute", headers=admin_headers, json=exec_payload)
    assert exec_res.status_code == 200
    summary = exec_res.json()
    assert summary["success"] is True
    assert summary["imported_count"] == 10
    assert summary["skipped_count"] == 0

    # Verify directly in PostgreSQL
    db_session.expire_all()
    for i in range(1, 11):
        adm = f"ADM-IMP-{tag}-{i:03d}"
        std = db_session.query(Student).filter(Student.admission_number == adm).first()
        assert std is not None
        assert std.status == "ACTIVE"
        assert std.gender == "Male"

        # Verify enrollment
        enr = db_session.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == std.id,
            StudentEnrollment.class_id == primary_class.id,
            StudentEnrollment.academic_year == "2026/2027",
        ).first()
        assert enr is not None
        assert enr.status == "ACTIVE"


# =============================================================================
# 4. FEES MODULE INTEGRATION VERIFICATION
# =============================================================================

def test_fees_module_retrieves_imported_students(client, admin_headers, primary_class):
    """Verify Fees module retrieves the exact enrolled students without fake records."""
    res = client.get(
        f"/api/v1/fees/classes/{primary_class.id}/students",
        headers=admin_headers,
        params={"academic_year": "2026/2027"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["class_id"] == primary_class.id
    assert data["total_students"] >= 10


# =============================================================================
# 5. DUPLICATE IMPORT & ENROLLMENT PROTECTION
# =============================================================================

def test_duplicate_import_protection(client, admin_headers, primary_class):
    """Uploading the same Excel file again must flag records as ALREADY_EXISTS / ALREADY ENROLLED."""
    tag = uuid.uuid4().hex[:5].upper()
    sample_students = [
        (f"Khadar{i}", "Ali", f"Warsame{tag}", "Male", "2012-01-10", "Ali Warsame", f"+25261520{i:04d}", "", "Father", "", "Mogadishu", f"ADM-DUP-{tag}-{i:03d}")
        for i in range(1, 11)
    ]
    excel_bytes = create_test_excel_bytes(sample_students)

    # Initial Import
    files1 = {"file": ("dup_test.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"class_id": primary_class.id, "academic_year": "2026/2027"}
    prev1 = client.post("/api/v1/students/import/preview", headers=admin_headers, files=files1, data=data)
    assert prev1.status_code == 200

    exec1 = client.post("/api/v1/students/import/execute", headers=admin_headers, json={
        "class_id": primary_class.id,
        "academic_year": "2026/2027",
        "file_name": "dup_test.xlsx",
        "rows": prev1.json()["rows"],
        "enroll_existing_students": False,
    })
    assert exec1.status_code == 200
    assert exec1.json()["imported_count"] == 10

    # Re-upload same file
    files2 = {"file": ("dup_test.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    prev_res = client.post("/api/v1/students/import/preview", headers=admin_headers, files=files2, data=data)
    assert prev_res.status_code == 200
    json_data = prev_res.json()
    assert json_data["already_exists_rows"] == 10
    assert json_data["valid_rows"] == 0

    # Executing import of duplicates must skip all and insert 0
    exec_payload = {
        "class_id": primary_class.id,
        "academic_year": "2026/2027",
        "file_name": "dup_test.xlsx",
        "rows": json_data["rows"],
        "enroll_existing_students": False,
    }
    exec_res = client.post("/api/v1/students/import/execute", headers=admin_headers, json=exec_payload)
    assert exec_res.status_code == 200
    summary = exec_res.json()
    assert summary["imported_count"] == 0
    assert summary["already_enrolled_count"] == 10
    assert summary["skipped_count"] == 10


# =============================================================================
# 6. INVALID ROW REJECTION & VALID ROW PARTIAL IMPORT
# =============================================================================

def test_invalid_rows_rejected_with_exact_reasons(client, admin_headers, primary_class):
    """Test validation errors for missing names, invalid gender, invalid phone, and valid partial import."""
    tag = uuid.uuid4().hex[:5].upper()
    mixed_students = [
        # 1. Valid
        (f"Saafi{tag}", "Hassan", "Geedi", "Female", "2013-02-14", "Hassan Geedi", "+252615777001", "", "Father", "", "Mogadishu", f"ADM-V1-{tag}"),
        # 2. Missing First Name
        ("", "Hassan", "Geedi", "Female", "2013-02-14", "Hassan Geedi", "+252615777002", "", "Father", "", "Mogadishu", f"ADM-INV2-{tag}"),
        # 3. Invalid Gender
        (f"Nuur{tag}", "Abdi", "Warsame", "Alien", "2013-05-18", "Abdi Warsame", "+252615777003", "", "Father", "", "Mogadishu", f"ADM-INV3-{tag}"),
        # 4. Missing Guardian Phone
        (f"Bilan{tag}", "Farah", "Ali", "Female", "2013-09-20", "Farah Ali", "", "", "Father", "", "Mogadishu", f"ADM-INV4-{tag}"),
        # 5. Valid
        (f"Guled{tag}", "Osman", "Dirie", "Male", "2013-11-12", "Osman Dirie", "+252615777005", "", "Father", "", "Mogadishu", f"ADM-V5-{tag}"),
    ]
    excel_bytes = create_test_excel_bytes(mixed_students)

    files = {"file": ("students_mixed.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"class_id": primary_class.id, "academic_year": "2026/2027"}

    prev_res = client.post("/api/v1/students/import/preview", headers=admin_headers, files=files, data=data)
    assert prev_res.status_code == 200
    json_data = prev_res.json()
    assert json_data["total_rows"] == 5
    assert json_data["valid_rows"] == 2
    assert json_data["error_rows"] == 3

    # Check error reasons
    rows = json_data["rows"]
    assert rows[0]["status"] == "VALID"
    assert rows[1]["status"] == "ERROR" and "First name is required" in rows[1]["error_reason"]
    assert rows[2]["status"] == "ERROR" and "Invalid gender" in rows[2]["error_reason"]
    assert rows[3]["status"] == "ERROR" and "Guardian phone is required" in rows[3]["error_reason"]
    assert rows[4]["status"] == "VALID"

    # Execute import of valid rows (invalid rows must be skipped safely)
    exec_payload = {
        "class_id": primary_class.id,
        "academic_year": "2026/2027",
        "file_name": "students_mixed.xlsx",
        "rows": rows,
        "enroll_existing_students": False,
    }
    exec_res = client.post("/api/v1/students/import/execute", headers=admin_headers, json=exec_payload)
    assert exec_res.status_code == 200
    summary = exec_res.json()
    assert summary["imported_count"] == 2
    assert summary["skipped_count"] == 3


# =============================================================================
# 7. RBAC & SECURITY TESTS
# =============================================================================

def test_teacher_cannot_import_students(client, teacher_headers, primary_class):
    """Teachers must be blocked from student import endpoints with HTTP 403."""
    excel_bytes = create_test_excel_bytes([("Test", "A", "B", "Male", "2012-01-01", "Guardian", "+252611111111", "", "", "", "", "ADM-SEC-01")])
    files = {"file": ("test.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"class_id": primary_class.id, "academic_year": "2026/2027"}

    res = client.post("/api/v1/students/import/preview", headers=teacher_headers, files=files, data=data)
    assert res.status_code == 403

    res_exec = client.post("/api/v1/students/import/execute", headers=teacher_headers, json={"class_id": primary_class.id, "academic_year": "2026/2027", "rows": []})
    assert res_exec.status_code == 403


def test_student_cannot_import_students(client, student_headers, primary_class):
    """Students must be blocked from student import endpoints with HTTP 403."""
    excel_bytes = create_test_excel_bytes([("Test", "A", "B", "Male", "2012-01-01", "Guardian", "+252611111111", "", "", "", "", "ADM-SEC-02")])
    files = {"file": ("test.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"class_id": primary_class.id, "academic_year": "2026/2027"}

    res = client.post("/api/v1/students/import/preview", headers=student_headers, files=files, data=data)
    assert res.status_code == 403


# =============================================================================
# 8. PRIMARY VS SECONDARY CLASS SCOPING ISOLATION
# =============================================================================

def test_primary_and_secondary_class_scoping_isolation(client, admin_headers, primary_class, secondary_class, db_session):
    """Importing into Secondary class Form 1-A must only enroll into Form 1-A, not Grade 8-A."""
    tag = uuid.uuid4().hex[:5].upper()
    secondary_students = [
        (f"Daud{tag}", "Omar", "Kahin", "Male", "2010-06-15", "Omar Kahin", "+252615999001", "", "Father", "", "Mogadishu", f"ADM-SEC-F1-{tag}-1"),
        (f"Sagal{tag}", "Ali", "Farah", "Female", "2010-08-20", "Ali Farah", "+252615999002", "", "Father", "", "Mogadishu", f"ADM-SEC-F1-{tag}-2"),
    ]
    excel_bytes = create_test_excel_bytes(secondary_students)

    files = {"file": ("form1_students.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"class_id": secondary_class.id, "academic_year": "2026/2027"}

    prev_res = client.post("/api/v1/students/import/preview", headers=admin_headers, files=files, data=data)
    assert prev_res.status_code == 200
    rows = prev_res.json()["rows"]

    exec_payload = {
        "class_id": secondary_class.id,
        "academic_year": "2026/2027",
        "file_name": "form1_students.xlsx",
        "rows": rows,
    }
    exec_res = client.post("/api/v1/students/import/execute", headers=admin_headers, json=exec_payload)
    assert exec_res.status_code == 200
    assert exec_res.json()["imported_count"] == 2

    # Verify Daud is enrolled in Form 1-A and NOT in Grade 8-A
    db_session.expire_all()
    daud = db_session.query(Student).filter(Student.admission_number == f"ADM-SEC-F1-{tag}-1").first()
    assert daud is not None
    form1_enr = db_session.query(StudentEnrollment).filter(
        StudentEnrollment.student_id == daud.id,
        StudentEnrollment.class_id == secondary_class.id,
    ).first()
    assert form1_enr is not None

    g8_enr = db_session.query(StudentEnrollment).filter(
        StudentEnrollment.student_id == daud.id,
        StudentEnrollment.class_id == primary_class.id,
    ).first()
    assert g8_enr is None


# =============================================================================
# 9. AUDIT HISTORY TEST
# =============================================================================

def test_import_history_audit_trail(client, admin_headers):
    """Verify import history returns the audit records of previous imports."""
    res = client.get("/api/v1/students/import/history", headers=admin_headers)
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) > 0
    assert logs[0]["file_name"] is not None
    assert logs[0]["academic_year"] == "2026/2027"

    # Also test /admin/students/import/history
    admin_res = client.get("/api/v1/admin/students/import/history", headers=admin_headers)
    assert admin_res.status_code == 200


# =============================================================================
# 10. ADMIN PREFIX ROUTES & EDGE CASE VALIDATIONS
# =============================================================================

def test_admin_prefixed_preview_and_import(client, admin_headers, primary_class):
    """Verify that routes under /api/v1/admin/students/import/preview and /api/v1/admin/students/import work cleanly."""
    tag = uuid.uuid4().hex[:5].upper()
    sample_students = [
        (f"AdminRouteStd{i}", "A", f"Test{tag}", "Male", "2013-03-10", "Parent Name", f"+25261544{i:04d}", "", "Father", "", "Mogadishu", f"ADM-ADMROUTE-{tag}-{i}")
        for i in range(1, 3)
    ]
    excel_bytes = create_test_excel_bytes(sample_students)

    # Preview on /api/v1/admin/students/import/preview with academic_year_id
    files = {"file": ("admin_route_test.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"class_id": primary_class.id, "academic_year_id": "2026/2027"}
    prev_res = client.post("/api/v1/admin/students/import/preview", headers=admin_headers, files=files, data=data)
    assert prev_res.status_code == 200
    preview_json = prev_res.json()
    assert preview_json["valid_rows"] == 2
    assert "destination" in preview_json
    assert "summary" in preview_json

    # Import via POST /api/v1/admin/students/import
    exec_res = client.post("/api/v1/admin/students/import", headers=admin_headers, json={
        "class_id": primary_class.id,
        "academic_year": "2026/2027",
        "file_name": "admin_route_test.xlsx",
        "rows": preview_json["rows"],
    })
    assert exec_res.status_code == 200
    assert exec_res.json()["imported_count"] == 2


def test_empty_excel_file_rejected(client, admin_headers, primary_class):
    """Uploading an Excel file with zero data rows must return a 400 Bad Request with clear explanation."""
    excel_bytes = create_test_excel_bytes([])  # Headers only, no data
    files = {"file": ("empty.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"class_id": primary_class.id, "academic_year": "2026/2027"}

    res = client.post("/api/v1/admin/students/import/preview", headers=admin_headers, files=files, data=data)
    assert res.status_code == 400
    assert "No student records were found in this Excel file" in res.json()["detail"]


def test_invalid_file_extension_rejected(client, admin_headers, primary_class):
    """Uploading a PDF or non-Excel file must be rejected with a 400 Bad Request."""
    files = {"file": ("document.pdf", b"%PDF-1.4 dummy content", "application/pdf")}
    data = {"class_id": primary_class.id, "academic_year": "2026/2027"}

    res = client.post("/api/v1/admin/students/import/preview", headers=admin_headers, files=files, data=data)
    assert res.status_code == 400
    assert "Invalid file type" in res.json()["detail"]


def test_missing_required_headers_rejected(client, admin_headers, primary_class):
    """Excel missing mandatory headers like guardian_phone must be rejected with detailed list."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["First Name", "Last Name"])  # Missing gender, guardian_name, guardian_phone
    ws.append(["Ali", "Hassan"])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    files = {"file": ("missing_cols.xlsx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"class_id": primary_class.id, "academic_year": "2026/2027"}

    res = client.post("/api/v1/admin/students/import/preview", headers=admin_headers, files=files, data=data)
    assert res.status_code == 400
    assert "Missing required columns" in res.json()["detail"]
