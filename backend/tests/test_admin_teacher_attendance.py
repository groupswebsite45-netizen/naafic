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
from app.models.teacher_attendance import TeacherAttendance

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
def teacher_headers():
    db = SessionLocal()
    teacher = db.query(Teacher).filter(Teacher.user_id.isnot(None), Teacher.status == "ACTIVE").first()
    if not teacher:
        pytest.skip("No active teacher with user account found.")
    user = db.query(User).filter(User.id == teacher.user_id).first()
    token = create_access_token(subject=str(user.id))
    db.close()
    return {"Authorization": f"Bearer {token}"}


def test_admin_get_teacher_daily_roster(admin_headers):
    """1. Test admin can fetch the daily roster of teachers."""
    today = date.today().isoformat()
    res = client.get(f"/api/v1/admin/teacher-attendance/roster?date={today}", headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "date" in data
    assert data["date"] == today
    assert "academic_year" in data
    assert "total_teachers" in data
    assert "teachers" in data
    assert isinstance(data["teachers"], list)
    if data["teachers"]:
        first = data["teachers"][0]
        assert "teacher_id" in first
        assert "teacher_name" in first
        assert "status" in first


def test_admin_save_daily_teacher_attendance(admin_headers):
    """2. Test admin can mark and save teacher attendance with reasons."""
    today = date.today().isoformat()
    # First get roster to have valid teacher IDs
    res_roster = client.get(f"/api/v1/admin/teacher-attendance/roster?date={today}", headers=admin_headers)
    assert res_roster.status_code == 200
    roster = res_roster.json()
    assert len(roster["teachers"]) > 0, "Expected at least one active teacher"

    entries_to_save = []
    statuses = ["PRESENT", "ABSENT", "LATE", "ON_LEAVE"]
    for i, item in enumerate(roster["teachers"]):
        status = statuses[i % len(statuses)]
        reason = f"Automated test note {status}" if status != "PRESENT" else None
        entries_to_save.append({
            "teacher_id": item["teacher_id"],
            "status": status,
            "reason": reason
        })

    payload = {
        "date": today,
        "academic_year": roster.get("academic_year") or "2026/2027",
        "entries": entries_to_save
    }

    res_save = client.post("/api/v1/admin/teacher-attendance/save", json=payload, headers=admin_headers)
    assert res_save.status_code == 200, res_save.text
    save_data = res_save.json()
    assert save_data["total_saved"] == len(entries_to_save)

    # Verify upsert / update: re-fetching roster reflects updated statuses
    res_roster_updated = client.get(f"/api/v1/admin/teacher-attendance/roster?date={today}", headers=admin_headers)
    assert res_roster_updated.status_code == 200
    updated_items = {it["teacher_id"]: it for it in res_roster_updated.json()["teachers"]}
    for req_item in entries_to_save:
        tid = req_item["teacher_id"]
        assert tid in updated_items
        assert updated_items[tid]["status"] == req_item["status"]
        if req_item["reason"]:
            assert updated_items[tid]["reason"] == req_item["reason"]


def test_prevent_future_date_submission(admin_headers):
    """3. Test that marking attendance for future dates is strictly rejected."""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    payload = {
        "date": tomorrow,
        "academic_year": "2026/2027",
        "entries": [
            {"teacher_id": 1, "status": "PRESENT", "reason": None}
        ]
    }
    res = client.post("/api/v1/admin/teacher-attendance/save", json=payload, headers=admin_headers)
    assert res.status_code in [400, 422], f"Expected 400/422 for future date, got {res.status_code}: {res.text}"


def test_teacher_attendance_dashboard(admin_headers):
    """4. Test that staff attendance dashboard KPIs and trends return accurately."""
    res = client.get("/api/v1/admin/teacher-attendance/dashboard", headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "kpis" in data
    kpis = data["kpis"]
    assert "total_teachers" in kpis
    assert "today_present" in kpis
    assert "today_absent" in kpis
    assert "today_late" in kpis
    assert "today_on_leave" in kpis
    assert "today_attendance_percentage" in kpis
    assert "daily_summary" in data
    assert isinstance(data["daily_summary"], list)
    assert "monthly_summary" in data
    assert isinstance(data["monthly_summary"], list)


def test_teacher_attendance_summary_and_records(admin_headers):
    """5. Test staff summary report and historical records filters."""
    # Staff summary
    res_sum = client.get("/api/v1/admin/teacher-attendance/summary", headers=admin_headers)
    assert res_sum.status_code == 200, res_sum.text
    sum_data = res_sum.json()
    assert "total_teachers" in sum_data
    assert "teachers" in sum_data
    assert isinstance(sum_data["teachers"], list)

    # Historical records log
    res_rec = client.get("/api/v1/admin/teacher-attendance/records?limit=20", headers=admin_headers)
    assert res_rec.status_code == 200, res_rec.text
    rec_data = res_rec.json()
    assert "total" in rec_data
    assert "items" in rec_data
    assert isinstance(rec_data["items"], list)


def test_teacher_attendance_excel_export(admin_headers):
    """6. Test Excel export of daily and staff summary teacher attendance."""
    today = date.today().isoformat()
    # Daily export
    res_daily = client.get(f"/api/v1/admin/teacher-attendance/export/excel?report_type=daily&date={today}", headers=admin_headers)
    assert res_daily.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in res_daily.headers["content-type"]
    wb = openpyxl.load_workbook(io.BytesIO(res_daily.content))
    assert len(wb.sheetnames) > 0

    # Summary export
    res_summary = client.get("/api/v1/admin/teacher-attendance/export/excel?report_type=staff_summary", headers=admin_headers)
    assert res_summary.status_code == 200
    wb2 = openpyxl.load_workbook(io.BytesIO(res_summary.content))
    assert len(wb2.sheetnames) > 0


def test_teacher_attendance_pdf_export(admin_headers):
    """7. Test PDF export of daily and staff summary teacher attendance."""
    today = date.today().isoformat()
    # Daily export
    res_daily = client.get(f"/api/v1/admin/teacher-attendance/export/pdf?report_type=daily&date={today}", headers=admin_headers)
    assert res_daily.status_code == 200
    assert "application/pdf" in res_daily.headers["content-type"]
    assert res_daily.content[:4] == b"%PDF"

    # Summary export
    res_summary = client.get("/api/v1/admin/teacher-attendance/export/pdf?report_type=staff_summary", headers=admin_headers)
    assert res_summary.status_code == 200
    assert "application/pdf" in res_summary.headers["content-type"]
    assert res_summary.content[:4] == b"%PDF"


def test_teacher_attendance_rbac_enforcement(teacher_headers, student_headers):
    """8. Test that teachers and students CANNOT access or manage teacher attendance."""
    # Teacher role attempting to access admin teacher attendance
    res_t = client.get("/api/v1/admin/teacher-attendance/dashboard", headers=teacher_headers)
    assert res_t.status_code == 403, f"Expected 403 for Teacher, got {res_t.status_code}"

    # Student role attempting to access admin teacher attendance
    res_s = client.get("/api/v1/admin/teacher-attendance/dashboard", headers=student_headers)
    assert res_s.status_code == 403, f"Expected 403 for Student, got {res_s.status_code}"
