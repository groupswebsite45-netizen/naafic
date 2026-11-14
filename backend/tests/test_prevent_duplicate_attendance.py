import pytest
from datetime import date, timedelta
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
from app.models.attendance import Attendance, AttendanceSubmission

client = TestClient(app)


@pytest.fixture(scope="module")
def attendance_setup():
    db = SessionLocal()
    teacher_role = db.query(Role).filter(Role.name == "TEACHER").first()

    # Subjects: Arabic & English
    arabic = db.query(Subject).filter(Subject.name == "Arabic").first()
    if not arabic:
        arabic = Subject(name="Arabic", code="ARB-LOCK-TEST")
        db.add(arabic)
        db.flush()

    english = db.query(Subject).filter(Subject.name == "English").first()
    if not english:
        english = Subject(name="English", code="ENG-LOCK-TEST")
        db.add(english)
        db.flush()

    # Dedicated isolated test class
    school_class = db.query(SchoolClass).filter(SchoolClass.code == "C1-LOCK").first()
    if not school_class:
        school_class = SchoolClass(
            name="Class 1 LockTest",
            code="C1-LOCK",
            academic_year="2026/2027",
            status="ACTIVE",
            capacity=40,
        )
        db.add(school_class)
        db.flush()

    # Student
    st = db.query(Student).filter(Student.admission_number == "STD-LOCK-01").first()
    if not st:
        st = Student(
            first_name="Hassan",
            last_name="LockStudent",
            admission_number="STD-LOCK-01",
            gender="M",
            status="ACTIVE",
        )
        db.add(st)
        db.flush()

    enr = db.query(StudentEnrollment).filter(
        StudentEnrollment.student_id == st.id,
        StudentEnrollment.class_id == school_class.id
    ).first()
    if not enr:
        enr = StudentEnrollment(
            student_id=st.id,
            class_id=school_class.id,
            academic_year="2026/2027",
            status="ACTIVE",
        )
        db.add(enr)
        db.flush()

    academic_year = "2026/2027"

    # Teacher user
    user = db.query(User).filter(User.username == "teacher_lock_tester").first()
    if not user:
        user = User(
            email="teacher_lock_test@hawlwadaagschool.edu.so",
            username="teacher_lock_tester",
            hashed_password=get_password_hash("LockPass@123"),
            full_name="Teacher Lock Tester",
            is_active=True,
        )
        db.add(user)
        db.flush()
        if teacher_role:
            db.add(UserRole(user_id=user.id, role_id=teacher_role.id))
            db.flush()
    else:
        user.email = "teacher_lock_test@hawlwadaagschool.edu.so"
        db.flush()

    teacher = db.query(Teacher).filter(Teacher.user_id == user.id).first()
    if not teacher:
        teacher = Teacher(
            user_id=user.id,
            first_name="Teacher",
            last_name="Lock Tester",
            email=user.email,
            gender="M",
            status="ACTIVE",
            teacher_number="T-LOCK-01",
        )
        db.add(teacher)
        db.flush()

    # Assign Teacher to Class for Arabic AND English
    for sub in [arabic, english]:
        asgn = db.query(TeacherAssignment).filter(
            TeacherAssignment.class_id == school_class.id,
            TeacherAssignment.subject_id == sub.id,
            TeacherAssignment.academic_year == academic_year
        ).first()
        if not asgn:
            asgn = TeacherAssignment(
                teacher_id=teacher.id,
                class_id=school_class.id,
                subject_id=sub.id,
                academic_year=academic_year,
                status="ACTIVE"
            )
            db.add(asgn)
        else:
            asgn.teacher_id = teacher.id
            asgn.status = "ACTIVE"

    db.commit()

    token = create_access_token(subject=str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "class_id": school_class.id,
        "class_name": school_class.name,
        "arabic_id": arabic.id,
        "english_id": english.id,
        "student_id": st.id,
        "academic_year": academic_year,
        "teacher_id": teacher.id,
        "user_id": user.id,
        "username": user.username,
        "headers": headers,
    }
    db.close()
    return data


def test_scenario_1_to_6_prevent_duplicate_daily_attendance(attendance_setup):
    """
    Test Scenarios 1 to 6 as explicitly requested:
    1. Teacher submits Class 1 – Arabic attendance on a date (e.g. today).
    2. Teacher returns to the same class, subject and date: attendance is visible but locked.
    3. Teacher cannot submit it a second time (backend rejects with 400).
    4. Teacher selects another subject (e.g. English): attendance can be submitted independently.
    5. Teacher selects another date (e.g. yesterday): attendance can be submitted if it does not already exist.
    6. Refreshing or logging out and back in must not remove the lock.
    """
    s = attendance_setup
    test_date = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    headers = s["headers"]

    # Pre-clean test records for test_date and yesterday
    db = SessionLocal()
    for d in [test_date, yesterday]:
        db.query(Attendance).filter(
            Attendance.class_id == s["class_id"],
            Attendance.subject_id.in_([s["arabic_id"], s["english_id"]]),
            Attendance.date == d
        ).delete(synchronize_session=False)
        db.query(AttendanceSubmission).filter(
            AttendanceSubmission.class_id == s["class_id"],
            AttendanceSubmission.subject_id.in_([s["arabic_id"], s["english_id"]]),
            AttendanceSubmission.date == d
        ).delete(synchronize_session=False)
    db.commit()
    db.close()

    # =========================================================================
    # SCENARIO 1: Teacher submits Class 1 – Arabic attendance on test_date
    # =========================================================================
    payload_arabic = {
        "class_id": s["class_id"],
        "subject_id": s["arabic_id"],
        "academic_year": s["academic_year"],
        "date": test_date,
        "entries": [
            {"student_id": s["student_id"], "status": "PRESENT", "remarks": "Prompt and attentive"}
        ]
    }
    res_sub1 = client.post("/api/v1/teacher-portal/attendance/save", json=payload_arabic, headers=headers)
    assert res_sub1.status_code == 200, res_sub1.text
    sub1_data = res_sub1.json()
    assert sub1_data["class_id"] == s["class_id"]
    assert sub1_data["subject_id"] == s["arabic_id"]
    assert sub1_data["present_count"] == 1

    # =========================================================================
    # SCENARIO 2: Teacher returns to the same class, subject and date:
    # attendance is visible but locked
    # =========================================================================
    roster_res = client.get(
        f"/api/v1/teacher-portal/attendance/roster?class_id={s['class_id']}&subject_id={s['arabic_id']}&date={test_date}&academic_year={s['academic_year']}",
        headers=headers
    )
    assert roster_res.status_code == 200
    roster_data = roster_res.json()
    assert roster_data["is_recorded"] is True
    assert roster_data["is_locked"] is True
    assert roster_data["submitted_at"] is not None
    # Student records are fully preserved and viewable
    student_record = next((st for st in roster_data["students"] if st["student_id"] == s["student_id"]), None)
    assert student_record is not None
    assert student_record["status"] == "PRESENT"
    assert student_record["remarks"] == "Prompt and attentive"

    # =========================================================================
    # SCENARIO 3: Teacher cannot submit it a second time (Backend protection)
    # =========================================================================
    payload_arabic_second = {
        "class_id": s["class_id"],
        "subject_id": s["arabic_id"],
        "academic_year": s["academic_year"],
        "date": test_date,
        "entries": [
            {"student_id": s["student_id"], "status": "ABSENT", "remarks": "Trying to overwrite"}
        ]
    }
    res_sub2 = client.post("/api/v1/teacher-portal/attendance/save", json=payload_arabic_second, headers=headers)
    assert res_sub2.status_code == 400
    error_detail = res_sub2.json()["detail"]
    assert "Attendance Already Submitted. You can view this record, but editing is not permitted." in error_detail

    # Verify original record in DB was NOT modified / overwritten
    db_verify = SessionLocal()
    att_rec = db_verify.query(Attendance).filter(
        Attendance.student_id == s["student_id"],
        Attendance.class_id == s["class_id"],
        Attendance.subject_id == s["arabic_id"],
        Attendance.date == test_date
    ).first()
    assert att_rec.status == "PRESENT"
    assert att_rec.remarks == "Prompt and attentive"
    db_verify.close()

    # =========================================================================
    # SCENARIO 4: Teacher selects another subject (English):
    # attendance can be submitted independently
    # =========================================================================
    payload_english = {
        "class_id": s["class_id"],
        "subject_id": s["english_id"],
        "academic_year": s["academic_year"],
        "date": test_date,
        "entries": [
            {"student_id": s["student_id"], "status": "ABSENT", "remarks": "Excused sick"}
        ]
    }
    res_eng = client.post("/api/v1/teacher-portal/attendance/save", json=payload_english, headers=headers)
    assert res_eng.status_code == 200, res_eng.text
    eng_data = res_eng.json()
    assert eng_data["subject_id"] == s["english_id"]
    assert eng_data["absent_count"] == 1

    # Verify both subjects now exist independently on the same date
    db_verify2 = SessionLocal()
    arb_in_db = db_verify2.query(Attendance).filter(
        Attendance.student_id == s["student_id"],
        Attendance.class_id == s["class_id"],
        Attendance.subject_id == s["arabic_id"],
        Attendance.date == test_date
    ).first()
    eng_in_db = db_verify2.query(Attendance).filter(
        Attendance.student_id == s["student_id"],
        Attendance.class_id == s["class_id"],
        Attendance.subject_id == s["english_id"],
        Attendance.date == test_date
    ).first()
    assert arb_in_db.status == "PRESENT"
    assert eng_in_db.status == "ABSENT"
    db_verify2.close()

    # =========================================================================
    # SCENARIO 5: Teacher selects another date (yesterday):
    # attendance can be submitted if it does not already exist
    # =========================================================================
    payload_yesterday = {
        "class_id": s["class_id"],
        "subject_id": s["arabic_id"],
        "academic_year": s["academic_year"],
        "date": yesterday,
        "entries": [
            {"student_id": s["student_id"], "status": "LATE", "remarks": "Late bus"}
        ]
    }
    res_yest = client.post("/api/v1/teacher-portal/attendance/save", json=payload_yesterday, headers=headers)
    assert res_yest.status_code == 200, res_yest.text
    yest_data = res_yest.json()
    assert yest_data["date"] == yesterday
    assert yest_data["late_count"] == 1

    # =========================================================================
    # SCENARIO 6: Refreshing or logging out and back in must not remove the lock
    # =========================================================================
    # Simulate fresh login with new JWT token
    login_res = client.post(
        "/api/v1/auth/login",
        json={"identifier": s["username"], "password": "LockPass@123"}
    )
    assert login_res.status_code == 200
    new_token = login_res.json()["access_token"]
    fresh_headers = {"Authorization": f"Bearer {new_token}"}

    # Fetch roster with new session
    fresh_roster = client.get(
        f"/api/v1/teacher-portal/attendance/roster?class_id={s['class_id']}&subject_id={s['arabic_id']}&date={test_date}",
        headers=fresh_headers
    )
    assert fresh_roster.status_code == 200
    fresh_data = fresh_roster.json()
    assert fresh_data["is_recorded"] is True
    assert fresh_data["is_locked"] is True

    # Attempt submission with fresh login -> still rejected
    fresh_sub = client.post("/api/v1/teacher-portal/attendance/save", json=payload_arabic, headers=fresh_headers)
    assert fresh_sub.status_code == 400
    assert "Attendance Already Submitted. You can view this record, but editing is not permitted." in fresh_sub.json()["detail"]


def test_concurrent_duplicate_submission_blocked_by_database_constraint(attendance_setup):
    """
    Test database constraint level protection against simultaneous / concurrent submissions.
    """
    s = attendance_setup
    unique_date = (date.today() - timedelta(days=10)).isoformat()

    db = SessionLocal()
    # Clean up
    db.query(Attendance).filter(
        Attendance.class_id == s["class_id"],
        Attendance.subject_id == s["arabic_id"],
        Attendance.date == unique_date
    ).delete(synchronize_session=False)
    db.query(AttendanceSubmission).filter(
        AttendanceSubmission.class_id == s["class_id"],
        AttendanceSubmission.subject_id == s["arabic_id"],
        AttendanceSubmission.date == unique_date
    ).delete(synchronize_session=False)
    db.commit()

    # Insert first submission directly into database
    sub1 = AttendanceSubmission(
        academic_year=s["academic_year"],
        class_id=s["class_id"],
        subject_id=s["arabic_id"],
        date=unique_date,
        period=None,
        teacher_id=s["teacher_id"],
        submitted_by_id=s["user_id"],
        status="SUBMITTED",
        total_students=1,
        present_count=1,
        late_count=0,
        absent_count=0
    )
    db.add(sub1)
    db.commit()

    # Now simulate a concurrent race condition inserting another AttendanceSubmission for the exact same session
    from sqlalchemy.exc import IntegrityError
    sub2 = AttendanceSubmission(
        academic_year=s["academic_year"],
        class_id=s["class_id"],
        subject_id=s["arabic_id"],
        date=unique_date,
        period=None,
        teacher_id=s["teacher_id"],
        submitted_by_id=s["user_id"],
        status="SUBMITTED",
        total_students=1,
        present_count=1,
        late_count=0,
        absent_count=0
    )
    db.add(sub2)
    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()
    db.close()
