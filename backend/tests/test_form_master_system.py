import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.exam import Exam, ExamResult
from app.models.attendance import Attendance
from app.models.fee import FeeStructure, StudentFee, FeePayment
from app.models.form_master import FormMasterAssignment
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.core.security import get_password_hash, create_access_token


@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _create_user_with_role(db, username: str, email: str, role_name: str) -> User:
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        role = Role(name=role_name, description=f"{role_name} role")
        db.add(role)
        db.commit()
        db.refresh(role)

    user = db.query(User).filter(User.username == username).first()
    if not user:
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash("Secret123!"),
            full_name=f"Test {username.capitalize()}",
            is_active=True,
            is_superuser=(role_name == "SUPER_ADMIN" or role_name == "ADMIN")
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        ur = UserRole(user_id=user.id, role_id=role.id)
        db.add(ur)
        db.commit()

    return user


def _auth_header(user: User) -> dict:
    token = create_access_token(subject=str(user.id), claims={"username": user.username})
    return {"Authorization": f"Bearer {token}"}


def test_form_master_complete_lifecycle(client: TestClient, db):
    academic_year = "2026/2027"

    # 1. Setup Admin User
    admin_user = _create_user_with_role(db, "admin_fm_test", "admin_fm@test.com", "ADMIN")
    admin_headers = _auth_header(admin_user)

    # 2. Setup 3 Teachers:
    # - ordinary_teacher (no FM assignment)
    # - fm_single (assigned to 1 class)
    # - fm_double (assigned to 2 classes)
    t1_user = _create_user_with_role(db, "teacher_ordinary", "t_ordinary@test.com", "TEACHER")
    t2_user = _create_user_with_role(db, "teacher_fm_single", "t_fmsingle@test.com", "TEACHER")
    t3_user = _create_user_with_role(db, "teacher_fm_double", "t_fmdouble@test.com", "TEACHER")

    t1 = db.query(Teacher).filter(Teacher.email == "t_ordinary@test.com").first()
    if not t1:
        t1 = Teacher(
            user_id=t1_user.id,
            teacher_number="TCH-FM-001",
            first_name="Ordinary",
            last_name="Teacher",
            gender="Male",
            email="t_ordinary@test.com",
            status="ACTIVE"
        )
        db.add(t1)
        db.commit()
        db.refresh(t1)

    t2 = db.query(Teacher).filter(Teacher.email == "t_fmsingle@test.com").first()
    if not t2:
        t2 = Teacher(
            user_id=t2_user.id,
            teacher_number="TCH-FM-002",
            first_name="SingleClass",
            last_name="Master",
            gender="Female",
            email="t_fmsingle@test.com",
            status="ACTIVE"
        )
        db.add(t2)
        db.commit()
        db.refresh(t2)

    t3 = db.query(Teacher).filter(Teacher.email == "t_fmdouble@test.com").first()
    if not t3:
        t3 = Teacher(
            user_id=t3_user.id,
            teacher_number="TCH-FM-003",
            first_name="DoubleClass",
            last_name="Master",
            gender="Male",
            email="t_fmdouble@test.com",
            status="ACTIVE"
        )
        db.add(t3)
        db.commit()
        db.refresh(t3)

    t1_headers = _auth_header(t1_user)
    t2_headers = _auth_header(t2_user)
    t3_headers = _auth_header(t3_user)

    # 3. Setup 4 distinct Classes
    classes = []
    for i, (name, code, div, lvl, sec) in enumerate([
        ("Form Master Class A", "FMA-2026", "PRIMARY", "Grade 7", "FM1"),
        ("Form Master Class B", "FMB-2026", "PRIMARY", "Grade 7", "FM2"),
        ("Form Master Class C", "FMC-2026", "SECONDARY", "Form 1", "FM3"),
        ("Form Master Class D", "FMD-2026", "SECONDARY", "Form 2", "FM4"),
    ]):
        sc = db.query(SchoolClass).filter(SchoolClass.code == code).first()
        if not sc:
            sc = SchoolClass(
                name=name,
                code=code,
                division=div,
                level=lvl,
                section=sec,
                academic_year=academic_year,
                capacity=40,
                status="ACTIVE"
            )
            db.add(sc)
            db.commit()
            db.refresh(sc)
        classes.append(sc)

    class_a, class_b, class_c, class_d = classes

    # 4. Setup Subjects
    sub_math = db.query(Subject).filter(Subject.code == "FM-MATH").first()
    if not sub_math:
        sub_math = Subject(name="FM Mathematics", code="FM-MATH", department="Science", status="ACTIVE")
        db.add(sub_math)
    sub_eng = db.query(Subject).filter(Subject.code == "FM-ENG").first()
    if not sub_eng:
        sub_eng = Subject(name="FM English", code="FM-ENG", department="Languages", status="ACTIVE")
        db.add(sub_eng)
    db.commit()
    db.refresh(sub_math)
    db.refresh(sub_eng)

    # 5. Setup Students for Class A
    st1 = db.query(Student).filter(Student.admission_number == "ADM-FM-001").first()
    if not st1:
        st1 = Student(
            admission_number="ADM-FM-001",
            first_name="Ahmed",
            last_name="Ali",
            gender="Male",
            status="ACTIVE",
            guardian_name="Ali Farah",
            guardian_phone="+252615000001"
        )
        db.add(st1)
        db.commit()
        db.refresh(st1)

    enr1 = db.query(StudentEnrollment).filter(
        StudentEnrollment.student_id == st1.id,
        StudentEnrollment.academic_year == academic_year
    ).first()
    if not enr1:
        enr1 = StudentEnrollment(
            student_id=st1.id,
            class_id=class_a.id,
            academic_year=academic_year,
            status="ACTIVE"
        )
        db.add(enr1)
        db.commit()

    # Create exam & exam results in Class A for Mathematics (taught by t1)
    exam1 = db.query(Exam).filter(
        Exam.class_id == class_a.id,
        Exam.subject_id == sub_math.id,
        Exam.academic_year == academic_year,
        Exam.exam_type == "Mid-Term"
    ).first()
    if not exam1:
        exam1 = Exam(
            name="Mid-Term Math 2026",
            exam_type="Mid-Term",
            academic_year=academic_year,
            class_id=class_a.id,
            subject_id=sub_math.id,
            teacher_id=t1.id,  # taught by ordinary teacher!
            start_date=date.today(),
            max_marks=100.0,
            pass_marks=50.0,
            status="PUBLISHED"
        )
        db.add(exam1)
        db.commit()
        db.refresh(exam1)

    res1 = db.query(ExamResult).filter(ExamResult.exam_id == exam1.id, ExamResult.student_id == st1.id).first()
    if not res1:
        res1 = ExamResult(
            exam_id=exam1.id,
            class_id=class_a.id,
            student_id=st1.id,
            subject_id=sub_math.id,
            marks_obtained=42.0,  # Below 50 -> poor performer!
            grade="F",
            attendance_status="PRESENT",
            status="RELEASED"
        )
        db.add(res1)
        db.commit()

    # Create attendance records for st1
    for day_offset in range(4):
        att_date = date.today() - timedelta(days=day_offset + 1)
        existing_att = db.query(Attendance).filter(
            Attendance.student_id == st1.id,
            Attendance.date == att_date,
            Attendance.subject_id == sub_math.id
        ).first()
        if not existing_att:
            att = Attendance(
                student_id=st1.id,
                class_id=class_a.id,
                subject_id=sub_math.id,
                teacher_id=t1.id,
                academic_year=academic_year,
                date=att_date,
                period="1",
                status="ABSENT" if day_offset < 3 else "PRESENT"  # 3 absences -> frequent absentee
            )
            db.add(att)
    db.commit()

    # Create fee for st1
    fee1 = db.query(StudentFee).filter(
        StudentFee.student_id == st1.id,
        StudentFee.academic_year == academic_year
    ).first()
    if not fee1:
        fee1 = StudentFee(
            invoice_number="INV-FM-001",
            student_id=st1.id,
            class_id=class_a.id,
            academic_year=academic_year,
            amount_due=150.0,
            due_date=date.today() - timedelta(days=5),  # Overdue
            status="OVERDUE"
        )
        db.add(fee1)
        db.commit()

    # Clean up any existing FM assignments for clean testing
    db.query(FormMasterAssignment).filter(
        FormMasterAssignment.academic_year == academic_year,
        FormMasterAssignment.class_id.in_([c.id for c in classes])
    ).delete(synchronize_session=False)
    db.commit()

    # =========================================================================
    # TEST 1: Ordinary teacher is NOT a Form Master
    # =========================================================================
    res = client.get("/api/v1/form-master/check", headers=t1_headers)
    assert res.status_code == 200
    assert res.json()["is_form_master"] is False
    assert res.json()["classes_count"] == 0

    res = client.get("/api/v1/form-master/my-classes", headers=t1_headers)
    assert res.status_code == 403
    assert "not an active Form Master" in res.json()["detail"]

    res = client.get(f"/api/v1/form-master/classes/{class_a.id}/dashboard", headers=t1_headers)
    assert res.status_code == 403

    # Ordinary teacher cannot access Admin Form Master endpoints
    res = client.get("/api/v1/form-masters/overview", headers=t1_headers)
    assert res.status_code == 403

    # =========================================================================
    # TEST 2: Admin Appoints Teacher 2 as Form Master for 1 class (Class A)
    # =========================================================================
    appoint_payload = {
        "teacher_id": t2.id,
        "class_ids": [class_a.id],
        "academic_year": academic_year,
        "notes": "Appointed Form Master for Grade 7A"
    }
    res = client.post("/api/v1/form-masters/appoint", json=appoint_payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert len(data) == 1
    assignment_a_id = data[0]["id"]
    assert data[0]["teacher_id"] == t2.id
    assert data[0]["class_id"] == class_a.id
    assert data[0]["status"] == "ACTIVE"

    # =========================================================================
    # TEST 3: Admin Appoints Teacher 3 as Form Master for 2 classes (Class B and Class C)
    # =========================================================================
    appoint_payload_2 = {
        "teacher_id": t3.id,
        "class_ids": [class_b.id, class_c.id],
        "academic_year": academic_year,
        "notes": "Supervising 2 classes"
    }
    res = client.post("/api/v1/form-masters/appoint", json=appoint_payload_2, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert len(data) == 2
    assert {d["class_id"] for d in data} == {class_b.id, class_c.id}

    # =========================================================================
    # TEST 4: Max 2 classes rule enforcement
    # Trying to assign a 3rd class (Class D) to Teacher 3 must be REJECTED (400)
    # =========================================================================
    res = client.post("/api/v1/form-masters/appoint", json={
        "teacher_id": t3.id,
        "class_ids": [class_d.id],
        "academic_year": academic_year
    }, headers=admin_headers)
    assert res.status_code == 400
    assert "Maximum allowed is 2 classes" in res.json()["detail"]

    # =========================================================================
    # TEST 5: Class duplicate assignment prevention
    # Class A already has an active Form Master (Teacher 2). Trying to appoint Teacher 1 must fail (400)
    # =========================================================================
    res = client.post("/api/v1/form-masters/appoint", json={
        "teacher_id": t1.id,
        "class_ids": [class_a.id],
        "academic_year": academic_year
    }, headers=admin_headers)
    assert res.status_code == 400
    assert "already assigned" in res.json()["detail"]

    # Duplicate in single list
    res = client.post("/api/v1/form-masters/appoint", json={
        "teacher_id": t1.id,
        "class_ids": [class_d.id, class_d.id],
        "academic_year": academic_year
    }, headers=admin_headers)
    assert res.status_code == 400
    assert "Duplicate class" in res.json()["detail"]

    # =========================================================================
    # TEST 6: Form Master 1 (Single Class - Class A) Portal Access & Supervision
    # =========================================================================
    # Pre-flight check
    res = client.get("/api/v1/form-master/check", headers=t2_headers)
    assert res.status_code == 200
    assert res.json()["is_form_master"] is True
    assert res.json()["classes_count"] == 1

    # List My Form Classes
    res = client.get("/api/v1/form-master/my-classes", headers=t2_headers)
    assert res.status_code == 200
    my_classes = res.json()
    assert len(my_classes) == 1
    assert my_classes[0]["id"] == class_a.id

    # Form Master 1 CANNOT access Class B or C (403 Forbidden)
    res = client.get(f"/api/v1/form-master/classes/{class_b.id}/dashboard", headers=t2_headers)
    assert res.status_code == 403
    assert "not officially assigned to you" in res.json()["detail"]

    # Form Master 1 Dashboard for Class A
    res = client.get(f"/api/v1/form-master/classes/{class_a.id}/dashboard", headers=t2_headers)
    assert res.status_code == 200
    dash = res.json()
    assert dash["total_students"] >= 1
    assert dash["students_with_poor_performance_count"] >= 1
    assert dash["students_with_frequent_absences_count"] >= 1
    assert dash["students_with_outstanding_fees_count"] >= 1
    assert len(dash["alerts"]) >= 1

    # Students Roster
    res = client.get(f"/api/v1/form-master/classes/{class_a.id}/students", headers=t2_headers)
    assert res.status_code == 200
    students_roster = res.json()
    assert len(students_roster) >= 1
    ahmed = next(s for s in students_roster if s["admission_number"] == "ADM-FM-001")
    assert ahmed["has_poor_academic_performance"] is True
    assert ahmed["has_frequent_absences"] is True
    assert ahmed["fee_balance"] > 0

    # Cross-Subject Results Monitoring (even though Math was taught by t1!)
    res = client.get(f"/api/v1/form-master/classes/{class_a.id}/results", headers=t2_headers)
    assert res.status_code == 200
    results_data = res.json()
    assert results_data["class_id"] == class_a.id
    assert results_data["poor_performers_count"] >= 1
    ahmed_res = next(s for s in results_data["students"] if s["admission_number"] == "ADM-FM-001")
    assert ahmed_res["is_poor_performer"] is True
    assert ahmed_res["subject_scores"][str(sub_math.id)]["marks"] == 42.0

    # Cross-Subject Attendance Monitoring
    res = client.get(f"/api/v1/form-master/classes/{class_a.id}/attendance", headers=t2_headers)
    assert res.status_code == 200
    att_data = res.json()
    assert att_data["class_id"] == class_a.id
    assert att_data["overall_stats"]["absent_count"] >= 3
    ahmed_att = next(s for s in att_data["students"] if s["admission_number"] == "ADM-FM-001")
    assert ahmed_att["is_frequent_absentee"] is True

    # Student Fees Monitoring (Read-Only)
    res = client.get(f"/api/v1/form-master/classes/{class_a.id}/fees", headers=t2_headers)
    assert res.status_code == 200
    fees_data = res.json()
    assert fees_data["summary"]["total_outstanding"] > 0
    ahmed_fee = next(s for s in fees_data["students"] if s["admission_number"] == "ADM-FM-001")
    assert ahmed_fee["balance"] == 150.0
    assert ahmed_fee["is_overdue"] is True

    # =========================================================================
    # TEST 7: Form Master 2 (Two Classes - Class B & Class C)
    # =========================================================================
    res = client.get("/api/v1/form-master/my-classes", headers=t3_headers)
    assert res.status_code == 200
    fm2_classes = res.json()
    assert len(fm2_classes) == 2
    fm2_ids = {c["id"] for c in fm2_classes}
    assert fm2_ids == {class_b.id, class_c.id}

    # Can access both Class B and Class C
    res_b = client.get(f"/api/v1/form-master/classes/{class_b.id}/dashboard", headers=t3_headers)
    assert res_b.status_code == 200
    res_c = client.get(f"/api/v1/form-master/classes/{class_c.id}/dashboard", headers=t3_headers)
    assert res_c.status_code == 200

    # CANNOT access Class A or Class D (403)
    res_a = client.get(f"/api/v1/form-master/classes/{class_a.id}/dashboard", headers=t3_headers)
    assert res_a.status_code == 403

    # =========================================================================
    # TEST 8: Admin Replaces Form Master for Class A
    # Replace Teacher 2 with Teacher 1
    # =========================================================================
    res = client.post(f"/api/v1/form-masters/{assignment_a_id}/replace", json={
        "new_teacher_id": t1.id,
        "notes": "Handover to Teacher 1"
    }, headers=admin_headers)
    assert res.status_code == 200
    new_assignment = res.json()
    assert new_assignment["teacher_id"] == t1.id
    assert new_assignment["class_id"] == class_a.id
    assert new_assignment["status"] == "ACTIVE"

    # Teacher 2 IMMEDIATELY loses Form Master access (403 Forbidden)
    res = client.get("/api/v1/form-master/my-classes", headers=t2_headers)
    assert res.status_code == 403
    res = client.get(f"/api/v1/form-master/classes/{class_a.id}/dashboard", headers=t2_headers)
    assert res.status_code == 403

    # Teacher 1 now has access!
    res = client.get("/api/v1/form-master/my-classes", headers=t1_headers)
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == class_a.id

    # =========================================================================
    # TEST 9: Admin Revokes Appointment
    # =========================================================================
    res = client.post(f"/api/v1/form-masters/{new_assignment['id']}/revoke", json={
        "notes": "Revoking appointment"
    }, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "REVOKED"

    # Teacher 1 IMMEDIATELY loses access
    res = client.get("/api/v1/form-master/my-classes", headers=t1_headers)
    assert res.status_code == 403
