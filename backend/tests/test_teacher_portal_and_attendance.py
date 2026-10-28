import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.attendance import Attendance
from app.models.exam import Exam, ExamResult

client = TestClient(app)


@pytest.fixture(scope="module")
def teacher_auth():
    # Find active teacher with user account
    db = SessionLocal()
    teacher = db.query(Teacher).filter(Teacher.user_id.isnot(None), Teacher.status == "ACTIVE").first()
    if not teacher:
        pytest.skip("No active teacher with user account found in PostgreSQL.")
    
    user = db.query(User).filter(User.id == teacher.user_id).first()
    db.close()

    # Login to get JWT
    from app.core.security import get_password_hash
    db = SessionLocal()
    u = db.query(User).filter(User.id == teacher.user_id).first()
    u.hashed_password = get_password_hash("TeacherTest@123")
    db.commit()
    db.close()

    login_res = client.post(
        "/api/v1/auth/login",
        json={"identifier": user.username, "password": "TeacherTest@123"}
    )

    assert login_res.status_code == 200, f"Teacher login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "teacher_id": teacher.id,
        "user_id": teacher.user_id,
        "username": user.username
    }


def test_teacher_dashboard_real_metrics(teacher_auth):
    headers = teacher_auth["headers"]
    res = client.get("/api/v1/teacher-portal/dashboard", headers=headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "total_classes" in data
    assert "total_subjects" in data
    assert "total_students" in data
    assert "today_attendance_summary" in data
    assert "pending_submissions" in data
    assert "assigned_classes" in data
    assert "upcoming_timetables" in data


def test_teacher_classes_and_detail(teacher_auth):
    headers = teacher_auth["headers"]
    res = client.get("/api/v1/teacher-portal/classes", headers=headers)
    assert res.status_code == 200
    classes = res.json()
    assert isinstance(classes, list)

    if classes:
        class_id = classes[0]["class_id"]
        detail_res = client.get(f"/api/v1/teacher-portal/classes/{class_id}/detail", headers=headers)
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["class_id"] == class_id
        assert "students" in detail
        assert "my_subjects" in detail
        assert "attendance_rate" in detail


def test_teacher_attendance_roster_defaults_to_present(teacher_auth):
    headers = teacher_auth["headers"]
    opts_res = client.get("/api/v1/teacher-portal/attendance/options", headers=headers)
    assert opts_res.status_code == 200
    opts = opts_res.json()
    
    if not opts["classes"] or not opts["subjects"]:
        pytest.skip("Teacher has no assigned classes or subjects.")

    target_class = opts["classes"][0]
    target_subject = next((s for s in opts["subjects"] if s["class_id"] == target_class["id"]), opts["subjects"][0])

    today_str = date.today().isoformat()
    roster_res = client.get(
        f"/api/v1/teacher-portal/attendance/roster?class_id={target_class['id']}&subject_id={target_subject['id']}&date={today_str}",
        headers=headers
    )
    assert roster_res.status_code == 200
    roster = roster_res.json()
    assert roster["class_id"] == target_class["id"]
    assert roster["subject_id"] == target_subject["id"]
    assert roster["date"] == today_str
    
    # All unrecorded students default to PRESENT
    for std in roster["students"]:
        if not roster["is_recorded"]:
            assert std["status"] == "PRESENT", f"Student {std['student_name']} did not default to PRESENT"


def test_teacher_save_attendance_postgresql_persistence(teacher_auth):
    headers = teacher_auth["headers"]
    opts = client.get("/api/v1/teacher-portal/attendance/options", headers=headers).json()
    if not opts["classes"] or not opts["subjects"]:
        pytest.skip("No assigned classes/subjects.")

    target_class = opts["classes"][0]
    target_subject = next((s for s in opts["subjects"] if s["class_id"] == target_class["id"]), opts["subjects"][0])
    today_str = date.today().isoformat()

    roster = client.get(
        f"/api/v1/teacher-portal/attendance/roster?class_id={target_class['id']}&subject_id={target_subject['id']}&date={today_str}",
        headers=headers
    ).json()

    if not roster["students"]:
        pytest.skip("No students enrolled in class.")

    # Mark first student absent with reason, others present
    entries = []
    for idx, s in enumerate(roster["students"]):
        if idx == 0:
            entries.append({"student_id": s["student_id"], "status": "ABSENT", "remarks": "Sick with flu"})
        else:
            entries.append({"student_id": s["student_id"], "status": "PRESENT", "remarks": None})

    payload = {
        "class_id": target_class["id"],
        "subject_id": target_subject["id"],
        "academic_year": target_class["academic_year"],
        "date": today_str,
        "period": None,
        "entries": entries
    }

    save_res = client.post("/api/v1/teacher-portal/attendance/save", json=payload, headers=headers)
    assert save_res.status_code == 200
    save_data = save_res.json()
    assert save_data["absent_count"] == 1
    assert save_data["present_count"] == len(entries) - 1

    # Verify directly in PostgreSQL
    db = SessionLocal()
    saved_absent = db.query(Attendance).filter(
        Attendance.student_id == entries[0]["student_id"],
        Attendance.class_id == target_class["id"],
        Attendance.subject_id == target_subject["id"],
        Attendance.date == date.today(),
        Attendance.period.is_(None)
    ).first()
    assert saved_absent is not None
    assert saved_absent.status == "ABSENT"
    assert saved_absent.remarks == "Sick with flu"
    db.close()


def test_teacher_attendance_future_date_rejected(teacher_auth):
    headers = teacher_auth["headers"]
    opts = client.get("/api/v1/teacher-portal/attendance/options", headers=headers).json()
    if not opts["classes"] or not opts["subjects"]:
        pytest.skip("No classes.")

    target_class = opts["classes"][0]
    target_subject = next((s for s in opts["subjects"] if s["class_id"] == target_class["id"]), opts["subjects"][0])
    future_date = (date.today() + timedelta(days=5)).isoformat()

    res = client.get(
        f"/api/v1/teacher-portal/attendance/roster?class_id={target_class['id']}&subject_id={target_subject['id']}&date={future_date}",
        headers=headers
    )
    assert res.status_code == 400
    assert "cannot be in the future" in res.text


def test_teacher_attendance_student_summary_calculation(teacher_auth):
    headers = teacher_auth["headers"]
    opts = client.get("/api/v1/teacher-portal/attendance/options", headers=headers).json()
    if not opts["classes"]:
        pytest.skip("No classes.")

    target_class = opts["classes"][0]
    res = client.get(
        f"/api/v1/teacher-portal/attendance/summary?class_id={target_class['id']}",
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["class_id"] == target_class["id"]
    assert "students" in data
    if data["students"]:
        s = data["students"][0]
        assert "attendance_percentage" in s
        assert "present_count" in s
        assert "absent_count" in s
        assert "absent_history" in s


def test_teacher_exam_paper_upload_and_removal(teacher_auth):
    headers = teacher_auth["headers"]
    exams_res = client.get("/api/v1/teacher-portal/exams", headers=headers)
    assert exams_res.status_code == 200
    exams = exams_res.json()

    if not exams:
        pytest.skip("No exams assigned to teacher.")

    exam = exams[0]
    exam_id = exam["id"]

    # Get roster
    roster_res = client.get(f"/api/v1/results/teacher/exams/{exam_id}/roster", headers=headers)
    if roster_res.status_code != 200:
        pytest.skip("Roster not accessible.")
    roster = roster_res.json()
    if not roster["students"]:
        pytest.skip("No students in exam roster.")

    student_id = roster["students"][0]["student_id"]

    # Upload test image
    file_content = b"%PDF-1.4 test exam paper content simulated bytes"
    files = {"file": ("student_exam_sheet.pdf", file_content, "application/pdf")}

    upload_res = client.post(
        f"/api/v1/teacher-portal/exams/{exam_id}/students/{student_id}/paper",
        files=files,
        headers=headers
    )
    assert upload_res.status_code == 200
    upload_data = upload_res.json()
    assert upload_data["filename"] == "student_exam_sheet.pdf"

    # Download test
    get_file_res = client.get(
        f"/api/v1/teacher-portal/exams/{exam_id}/students/{student_id}/paper",
        headers=headers
    )
    assert get_file_res.status_code == 200
    assert get_file_res.content == file_content

    # Delete test
    del_res = client.delete(
        f"/api/v1/teacher-portal/exams/{exam_id}/students/{student_id}/paper",
        headers=headers
    )
    assert del_res.status_code == 200
