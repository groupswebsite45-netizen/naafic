import pytest
from datetime import date
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.attendance import Attendance

client = TestClient(app)


@pytest.fixture(scope="module")
def admin_token():
    db = SessionLocal()
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        pytest.skip("No admin user found.")
    token = create_access_token(subject=str(admin_user.id))
    db.close()
    return token


@pytest.fixture(scope="module")
def subject_attendance_setup():
    """
    Sets up:
    - 1 Class: e.g. Class 1 / Grade 1 - A
    - 2 Subjects: Arabic and Mathematics
    - 2 Teachers: Teacher A (Arabic) and Teacher B (Mathematics)
    - 1 Active enrolled student
    """
    db = SessionLocal()

    # Get TEACHER role
    teacher_role = db.query(Role).filter(Role.name == "TEACHER").first()

    # Find or use Arabic and Mathematics subjects
    arabic_subj = db.query(Subject).filter(Subject.name == "Arabic").first()
    if not arabic_subj:
        arabic_subj = Subject(name="Arabic", code="ARB-TEST")
        db.add(arabic_subj)
        db.flush()

    math_subj = db.query(Subject).filter(Subject.name == "Mathematics").first()
    if not math_subj:
        math_subj = Subject(name="Mathematics", code="MATH-TEST")
        db.add(math_subj)
        db.flush()

    # Find an active class with enrolled students
    target_class = db.query(SchoolClass).first()
    if not target_class:
        pytest.skip("No school class found.")

    enrollment = db.query(StudentEnrollment).filter(
        StudentEnrollment.class_id == target_class.id,
        StudentEnrollment.status == "ACTIVE"
    ).first()
    if not enrollment:
        pytest.skip(f"No enrolled student found in class {target_class.name}")

    target_student = enrollment.student
    academic_year = enrollment.academic_year or target_class.academic_year or "2026/2027"

    # Teacher A for Arabic
    user_a = db.query(User).filter(User.username == "teacher_arabic_test").first()
    if not user_a:
        user_a = User(
            email="teacher_arabic@school.test",
            username="teacher_arabic_test",
            hashed_password=get_password_hash("TestPass@123"),
            full_name="Teacher A Arabic",
            is_active=True,
        )
        db.add(user_a)
        db.flush()
        if teacher_role:
            db.add(UserRole(user_id=user_a.id, role_id=teacher_role.id))
            db.flush()

    teacher_a = db.query(Teacher).filter(Teacher.user_id == user_a.id).first()
    if not teacher_a:
        teacher_a = Teacher(
            user_id=user_a.id,
            first_name="Teacher",
            last_name="A Arabic",
            email=user_a.email,
            gender="M",
            status="ACTIVE",
            teacher_number="T-ARB-01",
        )
        db.add(teacher_a)
        db.flush()

    # Teacher B for Mathematics
    user_b = db.query(User).filter(User.username == "teacher_math_test").first()
    if not user_b:
        user_b = User(
            email="teacher_math@school.test",
            username="teacher_math_test",
            hashed_password=get_password_hash("TestPass@123"),
            full_name="Teacher B Mathematics",
            is_active=True,
        )
        db.add(user_b)
        db.flush()
        if teacher_role:
            db.add(UserRole(user_id=user_b.id, role_id=teacher_role.id))
            db.flush()

    teacher_b = db.query(Teacher).filter(Teacher.user_id == user_b.id).first()
    if not teacher_b:
        teacher_b = Teacher(
            user_id=user_b.id,
            first_name="Teacher",
            last_name="B Math",
            email=user_b.email,
            gender="M",
            status="ACTIVE",
            teacher_number="T-MTH-02",
        )
        db.add(teacher_b)
        db.flush()

    # Create/ensure TeacherAssignment for Teacher A -> Class, Arabic
    asgn_a = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher_a.id,
        TeacherAssignment.class_id == target_class.id,
        TeacherAssignment.subject_id == arabic_subj.id
    ).first()
    if not asgn_a:
        asgn_a = TeacherAssignment(
            teacher_id=teacher_a.id,
            class_id=target_class.id,
            subject_id=arabic_subj.id,
            academic_year=academic_year,
            status="ACTIVE"
        )
        db.add(asgn_a)

    # Create/ensure TeacherAssignment for Teacher B -> Class, Mathematics
    asgn_b = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher_b.id,
        TeacherAssignment.class_id == target_class.id,
        TeacherAssignment.subject_id == math_subj.id
    ).first()
    if not asgn_b:
        asgn_b = TeacherAssignment(
            teacher_id=teacher_b.id,
            class_id=target_class.id,
            subject_id=math_subj.id,
            academic_year=academic_year,
            status="ACTIVE"
        )
        db.add(asgn_b)

    db.commit()

    token_a = create_access_token(subject=str(user_a.id))
    token_b = create_access_token(subject=str(user_b.id))

    setup_data = {
        "class_id": target_class.id,
        "class_name": target_class.name,
        "arabic_id": arabic_subj.id,
        "math_id": math_subj.id,
        "student_id": target_student.id,
        "student_name": target_student.full_name,
        "academic_year": academic_year,
        "teacher_a_id": teacher_a.id,
        "teacher_b_id": teacher_b.id,
        "headers_a": {"Authorization": f"Bearer {token_a}"},
        "headers_b": {"Authorization": f"Bearer {token_b}"},
    }
    db.close()
    return setup_data


def test_teacher_subject_authorization_isolation(subject_attendance_setup):
    """
    Verify Teacher A sees ONLY Arabic and Teacher B sees ONLY Mathematics.
    Ensure Teacher A CANNOT submit attendance for Mathematics (403 Forbidden).
    Ensure Teacher B CANNOT submit attendance for Arabic (403 Forbidden).
    """
    s = subject_attendance_setup
    today_str = date.today().isoformat()

    # Teacher A options
    res_a_opt = client.get("/api/v1/teacher-portal/attendance/options", headers=s["headers_a"])
    assert res_a_opt.status_code == 200
    a_subs = res_a_opt.json()["subjects"]
    assert any(sub["id"] == s["arabic_id"] for sub in a_subs)
    assert not any(sub["id"] == s["math_id"] for sub in a_subs)

    # Teacher B options
    res_b_opt = client.get("/api/v1/teacher-portal/attendance/options", headers=s["headers_b"])
    assert res_b_opt.status_code == 200
    b_subs = res_b_opt.json()["subjects"]
    assert any(sub["id"] == s["math_id"] for sub in b_subs)
    assert not any(sub["id"] == s["arabic_id"] for sub in b_subs)

    # Teacher A attempts to record for Mathematics -> 403 Forbidden
    unauthorized_payload = {
        "class_id": s["class_id"],
        "subject_id": s["math_id"],
        "academic_year": s["academic_year"],
        "date": today_str,
        "entries": [{"student_id": s["student_id"], "status": "PRESENT"}]
    }
    res_unauth = client.post(
        "/api/v1/teacher-portal/attendance/save",
        json=unauthorized_payload,
        headers=s["headers_a"]
    )
    assert res_unauth.status_code == 403, f"Expected 403, got {res_unauth.status_code}"

    # Teacher B attempts to record for Arabic -> 403 Forbidden
    unauthorized_payload_b = {
        "class_id": s["class_id"],
        "subject_id": s["arabic_id"],
        "academic_year": s["academic_year"],
        "date": today_str,
        "entries": [{"student_id": s["student_id"], "status": "PRESENT"}]
    }
    res_unauth_b = client.post(
        "/api/v1/teacher-portal/attendance/save",
        json=unauthorized_payload_b,
        headers=s["headers_b"]
    )
    assert res_unauth_b.status_code == 403, f"Expected 403, got {res_unauth_b.status_code}"


def test_independent_subject_attendance_same_day(subject_attendance_setup, admin_token):
    """
    CRITICAL REQUIREMENT:
    Test a student who attends Arabic but misses Mathematics on the same day.
    The system must show:
    - Arabic: Present
    - Mathematics: Absent
    Ensure one subject's attendance does NOT overwrite another subject's attendance.
    """
    s = subject_attendance_setup
    today_str = date.today().isoformat()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Clean up any previous test run records for today
    db_clean = SessionLocal()
    from app.models.attendance import AttendanceSubmission
    db_clean.query(Attendance).filter(
        Attendance.class_id == s["class_id"],
        Attendance.subject_id.in_([s["arabic_id"], s["math_id"]]),
        Attendance.date == date.today()
    ).delete(synchronize_session=False)
    db_clean.query(AttendanceSubmission).filter(
        AttendanceSubmission.class_id == s["class_id"],
        AttendanceSubmission.subject_id.in_([s["arabic_id"], s["math_id"]]),
        AttendanceSubmission.date == date.today()
    ).delete(synchronize_session=False)
    db_clean.commit()
    db_clean.close()

    # 1. Teacher A records Arabic as PRESENT
    payload_arabic = {
        "class_id": s["class_id"],
        "subject_id": s["arabic_id"],
        "academic_year": s["academic_year"],
        "date": today_str,
        "entries": [
            {"student_id": s["student_id"], "status": "PRESENT", "remarks": "Attended Arabic session"}
        ]
    }
    res_arb = client.post(
        "/api/v1/teacher-portal/attendance/save",
        json=payload_arabic,
        headers=s["headers_a"]
    )
    assert res_arb.status_code == 200, res_arb.text
    arb_data = res_arb.json()
    assert arb_data["present_count"] >= 1
    assert arb_data["subject_id"] == s["arabic_id"]

    # 2. Teacher B records Mathematics as ABSENT on the EXACT SAME DAY
    payload_math = {
        "class_id": s["class_id"],
        "subject_id": s["math_id"],
        "academic_year": s["academic_year"],
        "date": today_str,
        "entries": [
            {"student_id": s["student_id"], "status": "ABSENT", "remarks": "Missed Math session"}
        ]
    }
    res_math = client.post(
        "/api/v1/teacher-portal/attendance/save",
        json=payload_math,
        headers=s["headers_b"]
    )
    assert res_math.status_code == 200, res_math.text
    math_data = res_math.json()
    assert math_data["absent_count"] >= 1
    assert math_data["subject_id"] == s["math_id"]

    # Attempt duplicate submission for Arabic -> Must fail with 400
    res_arb_dup = client.post(
        "/api/v1/teacher-portal/attendance/save",
        json=payload_arabic,
        headers=s["headers_a"]
    )
    assert res_arb_dup.status_code == 400
    assert "Attendance Already Submitted" in res_arb_dup.text

    # 3. Direct DB Check: BOTH records must coexist independently!
    db = SessionLocal()
    att_arb = db.query(Attendance).filter(
        Attendance.student_id == s["student_id"],
        Attendance.class_id == s["class_id"],
        Attendance.subject_id == s["arabic_id"],
        Attendance.date == date.today()
    ).first()

    att_math = db.query(Attendance).filter(
        Attendance.student_id == s["student_id"],
        Attendance.class_id == s["class_id"],
        Attendance.subject_id == s["math_id"],
        Attendance.date == date.today()
    ).first()

    assert att_arb is not None, "Arabic attendance record was not persisted."
    assert att_math is not None, "Mathematics attendance record was not persisted."
    assert att_arb.status == "PRESENT", f"Expected Arabic PRESENT, got {att_arb.status}"
    assert att_math.status == "ABSENT", f"Expected Math ABSENT, got {att_math.status}"
    assert att_arb.id != att_math.id, "Records must be distinct database rows."
    db.close()

    # 4. Student Attendance Breakdown API Test (Both Admin and Teacher)
    # Admin endpoint
    res_breakdown = client.get(
        f"/api/v1/admin/attendance/students/{s['student_id']}/breakdown",
        headers=admin_headers
    )
    assert res_breakdown.status_code == 200, res_breakdown.text
    bd_data = res_breakdown.json()
    assert "by_subject" in bd_data
    assert "records" in bd_data

    # Find Arabic and Math in breakdown
    arb_summary = next((sub for sub in bd_data["by_subject"] if sub["subject_id"] == s["arabic_id"]), None)
    math_summary = next((sub for sub in bd_data["by_subject"] if sub["subject_id"] == s["math_id"]), None)

    assert arb_summary is not None, "Arabic not found in student subject breakdown"
    assert math_summary is not None, "Mathematics not found in student subject breakdown"

    assert arb_summary["present_count"] >= 1, "Arabic present_count should be at least 1"
    assert math_summary["absent_count"] >= 1, "Math absent_count should be at least 1"

    # Teacher A breakdown check (Teacher assigned to student's class)
    res_t_breakdown = client.get(
        f"/api/v1/teacher-portal/attendance/students/{s['student_id']}/breakdown",
        headers=s["headers_a"]
    )
    assert res_t_breakdown.status_code == 200, res_t_breakdown.text


def test_admin_subject_filtering_and_export(subject_attendance_setup, admin_token):
    """
    Verify Admin can:
    - Filter records by subject_id
    - Filter class reports by subject_id
    - Filter frequent absentees by subject_id
    - Export subject-based reports to Excel and PDF
    """
    s = subject_attendance_setup
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    today_str = date.today().isoformat()

    # 1. Admin records filtered by Arabic
    res_arb_recs = client.get(
        f"/api/v1/admin/attendance/records?class_id={s['class_id']}&subject_id={s['arabic_id']}&date={today_str}",
        headers=admin_headers
    )
    assert res_arb_recs.status_code == 200
    for r in res_arb_recs.json()["items"]:
        assert r["subject_id"] == s["arabic_id"]

    # 2. Admin records filtered by Math
    res_math_recs = client.get(
        f"/api/v1/admin/attendance/records?class_id={s['class_id']}&subject_id={s['math_id']}&date={today_str}",
        headers=admin_headers
    )
    assert res_math_recs.status_code == 200
    for r in res_math_recs.json()["items"]:
        assert r["subject_id"] == s["math_id"]

    # 3. Class report filtered by Subject
    res_cls_sub = client.get(
        f"/api/v1/admin/attendance/classes/{s['class_id']}/report?subject_id={s['arabic_id']}",
        headers=admin_headers
    )
    assert res_cls_sub.status_code == 200
    report_data = res_cls_sub.json()
    assert "students" in report_data
    # Each student includes subject_breakdown
    assert "subject_breakdown" in report_data["students"][0]

    # 4. Frequent absentees filtered by Mathematics
    res_freq = client.get(
        f"/api/v1/admin/attendance/frequent-absences?subject_id={s['math_id']}&threshold=1",
        headers=admin_headers
    )
    assert res_freq.status_code == 200

    # 5. Export Excel with subject_id
    res_excel = client.get(
        f"/api/v1/admin/attendance/export/excel?report_type=class_report&class_id={s['class_id']}&subject_id={s['arabic_id']}",
        headers=admin_headers
    )
    assert res_excel.status_code == 200
    assert len(res_excel.content) > 100

    # 6. Export PDF with subject_id
    res_pdf = client.get(
        f"/api/v1/admin/attendance/export/pdf?report_type=class_report&class_id={s['class_id']}&subject_id={s['arabic_id']}",
        headers=admin_headers
    )
    assert res_pdf.status_code == 200
    assert res_pdf.content.startswith(b"%PDF")
