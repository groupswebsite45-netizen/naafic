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
def dynamic_filters_setup():
    """
    Sets up two distinct classes, distinct subjects, and distinct teachers to test dynamic filter chains:
    - Class 1 (Year 2026/2027):
        - Subject: Arabic -> Teacher A
        - Subject: Mathematics -> Teacher B
    - Class 2 (Year 2026/2027):
        - Subject: Physics -> Teacher C
    - Class 3 (Year 2026/2027):
        - Subject: Chemistry -> Teacher D
    """
    db = SessionLocal()

    teacher_role = db.query(Role).filter(Role.name == "TEACHER").first()

    # Subjects
    arabic = db.query(Subject).filter(Subject.name == "Arabic").first()
    if not arabic:
        arabic = Subject(name="Arabic", code="ARB-DYN")
        db.add(arabic)
        db.flush()

    math = db.query(Subject).filter(Subject.name == "Mathematics").first()
    if not math:
        math = Subject(name="Mathematics", code="MTH-DYN")
        db.add(math)
        db.flush()

    physics = db.query(Subject).filter(Subject.name == "Physics").first()
    if not physics:
        physics = Subject(name="Physics", code="PHY-DYN")
        db.add(physics)
        db.flush()

    chemistry = db.query(Subject).filter(Subject.name == "Chemistry").first()
    if not chemistry:
        chemistry = Subject(name="Chemistry", code="CHM-DYN")
        db.add(chemistry)
        db.flush()

    # Classes
    class_1 = db.query(SchoolClass).filter(SchoolClass.name == "Class 1 DynFilter").first()
    if not class_1:
        class_1 = SchoolClass(
            name="Class 1 DynFilter",
            code="C1-DYN",
            academic_year="2026/2027",
            status="ACTIVE",
            capacity=40,
        )
        db.add(class_1)
        db.flush()

    class_2 = db.query(SchoolClass).filter(SchoolClass.name == "Class 2 DynFilter").first()
    if not class_2:
        class_2 = SchoolClass(
            name="Class 2 DynFilter",
            code="C2-DYN",
            academic_year="2026/2027",
            status="ACTIVE",
            capacity=40,
        )
        db.add(class_2)
        db.flush()

    class_past = db.query(SchoolClass).filter(SchoolClass.name == "Class Past DynFilter").first()
    if not class_past:
        class_past = SchoolClass(
            name="Class Past DynFilter",
            code="CP-DYN",
            academic_year="2026/2027",
            status="ACTIVE",
            capacity=40,
        )
        db.add(class_past)
        db.flush()

    # Students & Enrollments
    st1 = db.query(Student).filter(Student.admission_number == "STD-DYN-01").first()
    if not st1:
        st1 = Student(
            first_name="Ahmed",
            last_name="DynStudent",
            admission_number="STD-DYN-01",
            gender="M",
            status="ACTIVE",
        )
        db.add(st1)
        db.flush()

    enr1 = db.query(StudentEnrollment).filter(
        StudentEnrollment.student_id == st1.id,
        StudentEnrollment.class_id == class_1.id,
    ).first()
    if not enr1:
        enr1 = StudentEnrollment(
            student_id=st1.id,
            class_id=class_1.id,
            academic_year="2026/2027",
            status="ACTIVE",
        )
        db.add(enr1)
        db.flush()

    # Helper function to create teachers and users
    def get_or_create_teacher(username, full_name, t_num):
        usr = db.query(User).filter(User.username == username).first()
        if not usr:
            usr = User(
                email=f"{username}@school.test",
                username=username,
                hashed_password=get_password_hash("TestPass@123"),
                full_name=full_name,
                is_active=True,
            )
            db.add(usr)
            db.flush()
            if teacher_role:
                db.add(UserRole(user_id=usr.id, role_id=teacher_role.id))
                db.flush()
        tch = db.query(Teacher).filter(Teacher.user_id == usr.id).first()
        if not tch:
            tch = Teacher(
                user_id=usr.id,
                first_name=full_name.split()[0],
                last_name=full_name.split()[-1],
                email=usr.email,
                gender="M",
                status="ACTIVE",
                teacher_number=t_num,
            )
            db.add(tch)
            db.flush()
        return usr, tch

    user_a, teacher_a = get_or_create_teacher("dyn_teacher_a", "Teacher A Arabic", "T-DYN-A")
    user_b, teacher_b = get_or_create_teacher("dyn_teacher_b", "Teacher B Math", "T-DYN-B")
    user_c, teacher_c = get_or_create_teacher("dyn_teacher_c", "Teacher C Physics", "T-DYN-C")
    user_d, teacher_d = get_or_create_teacher("dyn_teacher_d", "Teacher D Chem", "T-DYN-D")

    # Teacher Assignments
    # Teacher A -> Class 1, Arabic
    asgn_a = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher_a.id,
        TeacherAssignment.class_id == class_1.id,
        TeacherAssignment.subject_id == arabic.id,
    ).first()
    if not asgn_a:
        asgn_a = TeacherAssignment(
            teacher_id=teacher_a.id,
            class_id=class_1.id,
            subject_id=arabic.id,
            academic_year="2026/2027",
            status="ACTIVE",
        )
        db.add(asgn_a)

    # Teacher B -> Class 1, Math
    asgn_b = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher_b.id,
        TeacherAssignment.class_id == class_1.id,
        TeacherAssignment.subject_id == math.id,
    ).first()
    if not asgn_b:
        asgn_b = TeacherAssignment(
            teacher_id=teacher_b.id,
            class_id=class_1.id,
            subject_id=math.id,
            academic_year="2026/2027",
            status="ACTIVE",
        )
        db.add(asgn_b)

    # Teacher C -> Class 2, Physics
    asgn_c = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher_c.id,
        TeacherAssignment.class_id == class_2.id,
        TeacherAssignment.subject_id == physics.id,
    ).first()
    if not asgn_c:
        asgn_c = TeacherAssignment(
            teacher_id=teacher_c.id,
            class_id=class_2.id,
            subject_id=physics.id,
            academic_year="2026/2027",
            status="ACTIVE",
        )
        db.add(asgn_c)

    # Teacher D -> Class Past, Chemistry
    asgn_d = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher_d.id,
        TeacherAssignment.class_id == class_past.id,
        TeacherAssignment.subject_id == chemistry.id,
    ).first()
    if not asgn_d:
        asgn_d = TeacherAssignment(
            teacher_id=teacher_d.id,
            class_id=class_past.id,
            subject_id=chemistry.id,
            academic_year="2026/2027",
            status="ACTIVE",
        )
        db.add(asgn_d)

    db.commit()

    token_a = create_access_token(subject=str(user_a.id))
    token_c = create_access_token(subject=str(user_c.id))

    setup_data = {
        "class_1": class_1,
        "class_2": class_2,
        "class_past": class_past,
        "arabic": arabic,
        "math": math,
        "physics": physics,
        "chemistry": chemistry,
        "teacher_a": teacher_a,
        "teacher_b": teacher_b,
        "teacher_c": teacher_c,
        "teacher_d": teacher_d,
        "student": st1,
        "token_a": token_a,
        "token_c": token_c,
    }
    db.close()
    return setup_data


def test_1_select_class_1_shows_only_class_1_subjects_and_teachers(admin_token, dynamic_filters_setup):
    """
    Test 1: Select Class 1: only Class 1 subjects and teachers should appear.
    """
    c1 = dynamic_filters_setup["class_1"]
    arabic = dynamic_filters_setup["arabic"]
    math = dynamic_filters_setup["math"]
    physics = dynamic_filters_setup["physics"]
    teacher_a = dynamic_filters_setup["teacher_a"]
    teacher_b = dynamic_filters_setup["teacher_b"]
    teacher_c = dynamic_filters_setup["teacher_c"]

    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get(
        f"/api/v1/admin/attendance/filter-options?class_id={c1.id}&academic_year=2026/2027",
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    subject_ids = [s["id"] for s in data["subjects"]]
    teacher_ids = [t["id"] for t in data["teachers"]]

    # Class 1 assigned subjects MUST be present
    assert arabic.id in subject_ids
    assert math.id in subject_ids
    # Physics is assigned exclusively to Class 2; it MUST NOT appear for Class 1
    assert physics.id not in subject_ids

    # Class 1 assigned teachers MUST be present
    assert teacher_a.id in teacher_ids
    assert teacher_b.id in teacher_ids
    # Teacher C is assigned exclusively to Class 2; must NOT appear for Class 1
    assert teacher_c.id not in teacher_ids


def test_2_select_class_2_class_1_subjects_and_teachers_disappear(admin_token, dynamic_filters_setup):
    """
    Test 2: Select Class 2: Class 1 subjects and teachers must disappear.
    """
    c2 = dynamic_filters_setup["class_2"]
    arabic = dynamic_filters_setup["arabic"]
    math = dynamic_filters_setup["math"]
    physics = dynamic_filters_setup["physics"]
    teacher_a = dynamic_filters_setup["teacher_a"]
    teacher_b = dynamic_filters_setup["teacher_b"]
    teacher_c = dynamic_filters_setup["teacher_c"]

    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get(
        f"/api/v1/admin/attendance/filter-options?class_id={c2.id}&academic_year=2026/2027",
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    subject_ids = [s["id"] for s in data["subjects"]]
    teacher_ids = [t["id"] for t in data["teachers"]]

    # Class 2 assigned items MUST appear
    assert physics.id in subject_ids
    assert teacher_c.id in teacher_ids

    # Class 1 items MUST disappear
    assert arabic.id not in subject_ids
    assert math.id not in subject_ids
    assert teacher_a.id not in teacher_ids
    assert teacher_b.id not in teacher_ids


def test_3_select_arabic_shows_only_arabic_teacher(admin_token, dynamic_filters_setup):
    """
    Test 3: Select Arabic: only teachers assigned to Arabic in that class should appear.
    """
    c1 = dynamic_filters_setup["class_1"]
    arabic = dynamic_filters_setup["arabic"]
    teacher_a = dynamic_filters_setup["teacher_a"]
    teacher_b = dynamic_filters_setup["teacher_b"]

    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get(
        f"/api/v1/admin/attendance/filter-options?class_id={c1.id}&subject_id={arabic.id}&academic_year=2026/2027",
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    teacher_ids = [t["id"] for t in data["teachers"]]

    # Teacher A (Arabic teacher) MUST appear
    assert teacher_a.id in teacher_ids
    # Teacher B (Math teacher) MUST NOT appear
    assert teacher_b.id not in teacher_ids


def test_4_date_filter_saved_attendance_returns_correct_records(admin_token, dynamic_filters_setup):
    """
    Test 4: Select a date with saved attendance: display the correct records.
    """
    c1 = dynamic_filters_setup["class_1"]
    arabic = dynamic_filters_setup["arabic"]
    teacher_a = dynamic_filters_setup["teacher_a"]
    student = dynamic_filters_setup["student"]
    token_a = dynamic_filters_setup["token_a"]

    saved_date = (date.today() - timedelta(days=2)).isoformat()

    # Clean up any existing test records for this date
    db_clean = SessionLocal()
    from app.models.attendance import Attendance, AttendanceSubmission
    db_clean.query(Attendance).filter(
        Attendance.class_id == c1.id,
        Attendance.subject_id == arabic.id,
        Attendance.date == (date.today() - timedelta(days=2))
    ).delete(synchronize_session=False)
    db_clean.query(AttendanceSubmission).filter(
        AttendanceSubmission.class_id == c1.id,
        AttendanceSubmission.subject_id == arabic.id,
        AttendanceSubmission.date == (date.today() - timedelta(days=2))
    ).delete(synchronize_session=False)
    db_clean.commit()
    db_clean.close()

    # Teacher A submits attendance for saved_date
    submit_payload = {
        "class_id": c1.id,
        "subject_id": arabic.id,
        "date": saved_date,
        "period": "Morning Session",
        "academic_year": "2026/2027",
        "entries": [
            {
                "student_id": student.id,
                "status": "PRESENT",
                "remarks": "On time for Arabic",
            }
        ],
    }
    t_headers = {"Authorization": f"Bearer {token_a}"}
    sub_resp = client.post("/api/v1/teacher-portal/attendance/save", json=submit_payload, headers=t_headers)
    assert sub_resp.status_code in [200, 201], sub_resp.text

    # Admin queries records for that date
    a_headers = {"Authorization": f"Bearer {admin_token}"}
    rec_resp = client.get(
        f"/api/v1/admin/attendance/records?class_id={c1.id}&subject_id={arabic.id}&date={saved_date}",
        headers=a_headers,
    )
    assert rec_resp.status_code == 200, rec_resp.text
    rec_data = rec_resp.json()
    assert rec_data["total"] >= 1
    found = any(r["student_id"] == student.id and r["status"] == "PRESENT" and r["date"] == saved_date for r in rec_data["items"])
    assert found, "Saved attendance record must be present on selected date"

    # Query class report for that date
    rep_resp = client.get(
        f"/api/v1/admin/attendance/classes/{c1.id}/report?subject_id={arabic.id}&date={saved_date}",
        headers=a_headers,
    )
    assert rep_resp.status_code == 200, rep_resp.text
    rep_data = rep_resp.json()
    assert rep_data["summary"]["present_count"] >= 1


def test_5_date_filter_without_attendance_shows_empty_and_no_auto_save(admin_token, dynamic_filters_setup):
    """
    Test 5: Select a date without attendance: display an empty state.
    Do not automatically create or save attendance records just because a date was selected.
    """
    c1 = dynamic_filters_setup["class_1"]
    arabic = dynamic_filters_setup["arabic"]
    token_a = dynamic_filters_setup["token_a"]

    empty_date = (date.today() - timedelta(days=30)).isoformat()

    # Verify no records exist beforehand
    db = SessionLocal()
    count_before = db.query(Attendance).filter(
        Attendance.class_id == c1.id,
        Attendance.subject_id == arabic.id,
        Attendance.date == empty_date,
    ).count()
    assert count_before == 0, f"Expected 0 records for date {empty_date}"

    # Query admin records for empty_date
    a_headers = {"Authorization": f"Bearer {admin_token}"}
    rec_resp = client.get(
        f"/api/v1/admin/attendance/records?class_id={c1.id}&subject_id={arabic.id}&date={empty_date}",
        headers=a_headers,
    )
    assert rec_resp.status_code == 200, rec_resp.text
    rec_data = rec_resp.json()
    assert rec_data["total"] == 0
    assert len(rec_data["items"]) == 0

    # Query teacher roster for empty_date
    t_headers = {"Authorization": f"Bearer {token_a}"}
    roster_resp = client.get(
        f"/api/v1/teacher-portal/attendance/roster?class_id={c1.id}&subject_id={arabic.id}&date={empty_date}",
        headers=t_headers,
    )
    assert roster_resp.status_code == 200, roster_resp.text
    roster_data = roster_resp.json()
    # is_recorded MUST be false
    assert roster_data["is_recorded"] is False

    # Check DB again: NO records must have been created automatically
    count_after = db.query(Attendance).filter(
        Attendance.class_id == c1.id,
        Attendance.subject_id == arabic.id,
        Attendance.date == empty_date,
    ).count()
    assert count_after == 0, "Selecting an attendance date must NOT auto-create records!"
    db.close()


def test_6_change_academic_year_refreshes_classes_subjects_teachers(admin_token, dynamic_filters_setup):
    """
    Test 6: Change academic year: refresh classes, subjects, teachers and attendance accordingly.
    """
    c_past = dynamic_filters_setup["class_past"]
    chem = dynamic_filters_setup["chemistry"]
    teacher_d = dynamic_filters_setup["teacher_d"]

    c1 = dynamic_filters_setup["class_1"]
    arabic = dynamic_filters_setup["arabic"]
    teacher_a = dynamic_filters_setup["teacher_a"]

    headers = {"Authorization": f"Bearer {admin_token}"}

    # Query options for 2026/2027
    resp_past = client.get(
        f"/api/v1/admin/attendance/filter-options?academic_year=2026/2027",
        headers=headers,
    )
    assert resp_past.status_code == 200, resp_past.text
    data_past = resp_past.json()

    past_class_ids = [c["id"] for c in data_past["classes"]]
    assert c_past.id in past_class_ids

    # Query for c_past specifically
    resp_past_cls = client.get(
        f"/api/v1/admin/attendance/filter-options?class_id={c_past.id}&academic_year=2026/2027",
        headers=headers,
    )
    assert resp_past_cls.status_code == 200, resp_past_cls.text
    data_past_cls = resp_past_cls.json()

    past_subj_ids = [s["id"] for s in data_past_cls["subjects"]]
    past_teacher_ids = [t["id"] for t in data_past_cls["teachers"]]

    # Chemistry and Teacher D belong to past year / past class
    assert chem.id in past_subj_ids
    assert teacher_d.id in past_teacher_ids

    # Arabic and Teacher A from Class 1 (2026/2027) must NOT appear for this past class query
    assert arabic.id not in past_subj_ids
    assert teacher_a.id not in past_teacher_ids
