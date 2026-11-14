import io
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
import openpyxl

from app.main import app
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.user import User
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.student_enrollment import StudentEnrollment
from app.models.attendance import Attendance

client = TestClient(app)


@pytest.fixture(scope="module")
def admin_headers():
    db = SessionLocal()
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        pytest.skip("No admin user found.")
    token = create_access_token(subject=str(admin_user.id))
    db.close()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def student_headers():
    db = SessionLocal()
    std = db.query(Student).filter(Student.user_id.isnot(None)).first()
    if std and std.user_id:
        std_user = db.query(User).filter(User.id == std.user_id).first()
    else:
        all_users = db.query(User).all()
        std_user = next((u for u in all_users if u.has_role("STUDENT")), None)
    if not std_user:
        pytest.skip("No student user found.")
    token = create_access_token(subject=str(std_user.id))
    db.close()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def teacher_auth():
    db = SessionLocal()
    teacher = db.query(Teacher).filter(Teacher.user_id.isnot(None), Teacher.status == "ACTIVE").first()
    if not teacher:
        pytest.skip("No active teacher with user account found.")
    user = db.query(User).filter(User.id == teacher.user_id).first()
    token = create_access_token(subject=str(user.id))
    
    # Also find an active assignment
    assignment = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher.id,
        TeacherAssignment.status == "ACTIVE"
    ).first()
    
    db.close()
    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "teacher_id": teacher.id,
        "user_id": teacher.user_id,
        "assignment": assignment,
    }


def test_admin_attendance_filter_options(admin_headers):
    """1. Test that filter options endpoint returns real academic years, classes, and subjects."""
    res = client.get("/api/v1/admin/attendance/filter-options", headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "academic_years" in data
    assert "classes" in data
    assert "subjects" in data
    assert "months" in data
    assert len(data["months"]) == 12
    assert len(data["classes"]) > 0


def test_admin_attendance_dashboard_real_metrics(admin_headers):
    """2. Test that attendance dashboard computes KPIs, trends, and summaries from PostgreSQL."""
    res = client.get("/api/v1/admin/attendance/dashboard", headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    kpis = data["kpis"]
    assert "total_students" in kpis
    assert "today_present" in kpis
    assert "today_absent" in kpis
    assert "today_late" in kpis
    assert "overall_attendance_percentage" in kpis
    assert "frequent_absentees_count" in kpis
    assert isinstance(data["daily_summary"], list)
    assert isinstance(data["weekly_summary"], list)
    assert isinstance(data["monthly_summary"], list)
    assert isinstance(data["recent_sessions"], list)


def test_admin_attendance_historical_records_filtering(admin_headers):
    """3. Test historical attendance records query with filters for class, status, and pagination."""
    res = client.get("/api/v1/admin/attendance/records?page=1&page_size=20", headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert "total_pages" in data

    # Test filtering by status
    res_absent = client.get("/api/v1/admin/attendance/records?status=ABSENT", headers=admin_headers)
    assert res_absent.status_code == 200
    absent_items = res_absent.json()["items"]
    for item in absent_items:
        assert item["status"] == "ABSENT"


def test_admin_attendance_class_report(admin_headers):
    """4. Test class-based attendance report with enrolled student percentages and absence dates."""
    db = SessionLocal()
    # Find a class with attendance records
    att = db.query(Attendance).first()
    if not att:
        db.close()
        pytest.skip("No attendance records found.")
    target_class_id = att.class_id
    db.close()

    res = client.get(f"/api/v1/admin/attendance/classes/{target_class_id}/report", headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["class_info"]["id"] == target_class_id
    assert "summary" in data
    assert "students" in data
    assert "dates_header" in data
    assert len(data["students"]) > 0

    first_student = data["students"][0]
    assert "attendance_percentage" in first_student
    assert "days_present" in first_student
    assert "days_absent" in first_student
    assert "absence_dates" in first_student


def test_admin_attendance_frequent_absentees_detection(admin_headers):
    """5. Test frequent absence detection ranking students by total absences."""
    res = client.get("/api/v1/admin/attendance/frequent-absences?threshold=1", headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert isinstance(data, list)
    if len(data) > 0:
        first = data[0]
        assert "student_name" in first
        assert "admission_number" in first
        assert "absent_count" in first
        assert first["absent_count"] >= 1
        assert "absence_dates" in first
        assert "guardian_phone" in first


def test_admin_attendance_export_excel(admin_headers):
    """6. Test generating and downloading styled Excel (.xlsx) attendance report."""
    db = SessionLocal()
    att = db.query(Attendance).first()
    if not att:
        db.close()
        pytest.skip("No attendance records.")
    class_id = att.class_id
    db.close()

    # Test class report Excel export
    res = client.get(
        f"/api/v1/admin/attendance/export/excel?report_type=class_report&class_id={class_id}",
        headers=admin_headers
    )
    assert res.status_code == 200, res.text
    assert "spreadsheetml.sheet" in res.headers["content-type"]
    wb = openpyxl.load_workbook(io.BytesIO(res.content))
    assert "Class Attendance Report" in wb.sheetnames

    # Test frequent absentees Excel export
    res_freq = client.get(
        "/api/v1/admin/attendance/export/excel?report_type=frequent_absentees&threshold=1",
        headers=admin_headers
    )
    assert res_freq.status_code == 200
    wb2 = openpyxl.load_workbook(io.BytesIO(res_freq.content))
    assert "Frequent Absentees" in wb2.sheetnames


def test_admin_attendance_export_pdf(admin_headers):
    """7. Test generating and downloading official PDF attendance report."""
    db = SessionLocal()
    att = db.query(Attendance).first()
    if not att:
        db.close()
        pytest.skip("No attendance records.")
    class_id = att.class_id
    db.close()

    # Test class report PDF export
    res = client.get(
        f"/api/v1/admin/attendance/export/pdf?report_type=class_report&class_id={class_id}",
        headers=admin_headers
    )
    assert res.status_code == 200, res.text
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF"), "Must be a valid PDF file"

    # Test frequent absentees PDF export
    res_freq = client.get(
        "/api/v1/admin/attendance/export/pdf?report_type=frequent_absentees&threshold=1",
        headers=admin_headers
    )
    assert res_freq.status_code == 200
    assert res_freq.content.startswith(b"%PDF")


def test_prevent_future_attendance_submission(teacher_auth):
    """8. Test that future attendance records are strictly rejected at backend."""
    if not teacher_auth["assignment"]:
        pytest.skip("No active teacher assignment.")

    assignment = teacher_auth["assignment"]
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    future_date = (date.today() + timedelta(days=7)).isoformat()

    # Test 1: Pydantic schema / service rejection for future date in save
    payload = {
        "class_id": assignment.class_id,
        "subject_id": assignment.subject_id,
        "academic_year": assignment.academic_year,
        "date": future_date,
        "entries": [
            {"student_id": 1, "status": "PRESENT"}
        ]
    }

    res = client.post(
        "/api/v1/teacher-portal/attendance/save",
        json=payload,
        headers=teacher_auth["headers"]
    )
    # Must reject with 400 Bad Request or 422 Unprocessable Entity
    assert res.status_code in [400, 422], f"Expected 400 or 422, got {res.status_code}: {res.text}"

    # Test 2: Roster lookup for future date must also reject
    res_roster = client.get(
        f"/api/v1/teacher-portal/attendance/roster?class_id={assignment.class_id}&subject_id={assignment.subject_id}&date={tomorrow}",
        headers=teacher_auth["headers"]
    )
    assert res_roster.status_code == 400
    assert "future" in res_roster.json()["detail"].lower()


def test_teacher_attendance_submission_reflected_in_admin(teacher_auth, admin_headers):
    """9. Test that attendance submitted by teacher immediately appears in Admin Attendance monitoring."""
    if not teacher_auth["assignment"]:
        pytest.skip("No active teacher assignment.")

    assignment = teacher_auth["assignment"]
    today_str = date.today().isoformat()

    # Get active enrolled student for this class
    db = SessionLocal()
    enrollment = db.query(StudentEnrollment).filter(
        StudentEnrollment.class_id == assignment.class_id,
        StudentEnrollment.status == "ACTIVE"
    ).first()
    if not enrollment:
        db.close()
        pytest.skip("No enrolled student found for assignment class.")
    student_id = enrollment.student_id
    db.close()

    # Clean up any existing test attendance for today
    db_clean = SessionLocal()
    from app.models.attendance import AttendanceSubmission
    db_clean.query(Attendance).filter(
        Attendance.class_id == assignment.class_id,
        Attendance.subject_id == assignment.subject_id,
        Attendance.date == date.today()
    ).delete(synchronize_session=False)
    db_clean.query(AttendanceSubmission).filter(
        AttendanceSubmission.class_id == assignment.class_id,
        AttendanceSubmission.subject_id == assignment.subject_id,
        AttendanceSubmission.date == date.today()
    ).delete(synchronize_session=False)
    db_clean.commit()
    db_clean.close()

    # Teacher saves attendance for today
    save_payload = {
        "class_id": assignment.class_id,
        "subject_id": assignment.subject_id,
        "academic_year": assignment.academic_year,
        "date": today_str,
        "entries": [
            {"student_id": student_id, "status": "PRESENT", "remarks": "Automated verification"}
        ]
    }
    save_res = client.post(
        "/api/v1/teacher-portal/attendance/save",
        json=save_payload,
        headers=teacher_auth["headers"]
    )
    assert save_res.status_code == 200, save_res.text

    # Admin verifies the record exists immediately
    admin_rec_res = client.get(
        f"/api/v1/admin/attendance/records?class_id={assignment.class_id}&student_id={student_id}&start_date={today_str}&end_date={today_str}",
        headers=admin_headers
    )
    assert admin_rec_res.status_code == 200
    items = admin_rec_res.json()["items"]
    assert any(
        item["student_id"] == student_id and item["date"] == today_str and item["status"] == "PRESENT"
        for item in items
    ), "Submitted teacher attendance must be immediately visible to Admin"


def test_security_admin_attendance_rbac_forbidden_for_non_admin(student_headers):
    """10. Test that non-admin users (e.g. students) cannot access Admin Attendance endpoints."""
    endpoints = [
        "/api/v1/admin/attendance/dashboard",
        "/api/v1/admin/attendance/records",
        "/api/v1/admin/attendance/classes/1/report",
        "/api/v1/admin/attendance/frequent-absences",
        "/api/v1/admin/attendance/export/excel?report_type=frequent_absentees",
        "/api/v1/admin/attendance/export/pdf?report_type=frequent_absentees",
    ]

    for ep in endpoints:
        res = client.get(ep, headers=student_headers)
        assert res.status_code == 403, f"Expected 403 Forbidden for endpoint {ep}, got {res.status_code}"
