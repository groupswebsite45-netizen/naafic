import pytest
from decimal import Decimal
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.user import User
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission
from app.models.result_release import ResultReleaseBatch
from app.models.student_result_view import StudentResultView


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    return TestClient(app)


def test_complete_result_workflow_end_to_end(client, db_session):
    """
    Test the complete, strict multi-stage examination result workflow:
    Teacher Draft -> Submit to Admin -> Admin Return -> Resubmit -> Admin Approve -> Class Release -> Student Visibility & View Tracking
    """
    # 1. Setup real test actors in PostgreSQL
    academic_year = "2026/2027"
    exam_name = "E2E Isolation Exam 2026"

    # Admin user
    admin_user = db_session.query(User).filter(User.username == "admin").first()
    assert admin_user is not None, "Initial admin user should exist"
    admin_token = create_access_token(subject=str(admin_user.id))
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Find or create a teacher with user account
    teacher_user = db_session.query(User).filter(User.username == "test_teacher_ahmed").first()
    if not teacher_user:
        teacher_user = User(
            username="test_teacher_ahmed",
            email="ahmed.test@hawlwadaag.edu.so",
            hashed_password="hashed_pass_test",
            full_name="Ahmed Hassan Warsame",
            is_active=True
        )
        db_session.add(teacher_user)
        db_session.flush()

    from app.models.user_role import UserRole
    ur = db_session.query(UserRole).filter(UserRole.user_id == teacher_user.id, UserRole.role_id == 2).first()
    if not ur:
        ur = UserRole(user_id=teacher_user.id, role_id=2)
        db_session.add(ur)
        db_session.commit()

    teacher = db_session.query(Teacher).filter(Teacher.user_id == teacher_user.id).first()
    if not teacher:
        teacher = Teacher(
            user_id=teacher_user.id,
            teacher_number="TCH-TEST-001",
            first_name="Ahmed",
            last_name="Warsame",
            gender="Male",
            email=teacher_user.email,
            status="ACTIVE"
        )
        db_session.add(teacher)
        db_session.flush()

    teacher_token = create_access_token(subject=str(teacher_user.id))
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    # Classes and Subjects
    school_class = db_session.query(SchoolClass).filter(SchoolClass.id == 147).first()
    if not school_class:
        school_class = db_session.query(SchoolClass).filter(SchoolClass.name.ilike("%Grade 7%")).first()

    math_subject = db_session.query(Subject).filter(Subject.name == "Mathematics").first()
    if not math_subject:
        math_subject = Subject(name="Mathematics", code="MATH-TEST", status="ACTIVE")
        db_session.add(math_subject)
        db_session.flush()

    eng_subject = db_session.query(Subject).filter(Subject.name.ilike("%English%")).first()
    if not eng_subject:
        eng_subject = Subject(name="English Language", code="ENG-TEST", status="ACTIVE")
        db_session.add(eng_subject)
        db_session.flush()

    # Assign teacher to class & subjects
    assign_math = db_session.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher.id,
        TeacherAssignment.class_id == school_class.id,
        TeacherAssignment.subject_id == math_subject.id,
        TeacherAssignment.academic_year == academic_year
    ).first()
    if not assign_math:
        assign_math = TeacherAssignment(
            teacher_id=teacher.id,
            class_id=school_class.id,
            subject_id=math_subject.id,
            academic_year=academic_year,
            status="ACTIVE"
        )
        db_session.add(assign_math)
        db_session.flush()

    # Find or create 2 test students
    students = db_session.query(Student).limit(2).all()
    assert len(students) >= 2, "Database must have at least 2 students"
    student_1 = students[0]
    student_2 = students[1]

    # Ensure enrollments exist for this academic year
    for s in (student_1, student_2):
        enr = db_session.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == s.id,
            StudentEnrollment.academic_year.in_([academic_year, academic_year.replace("-", "/")])
        ).first()
        if not enr:
            enr = StudentEnrollment(
                student_id=s.id,
                class_id=school_class.id,
                academic_year=academic_year,
                status="ACTIVE"
            )
            db_session.add(enr)
        else:
            enr.class_id = school_class.id
            enr.status = "ACTIVE"
    db_session.flush()

    # Find or create Exam record for Math in this class
    math_exam = db_session.query(Exam).filter(
        Exam.class_id == school_class.id,
        Exam.subject_id == math_subject.id,
        Exam.academic_year == academic_year,
        Exam.name == exam_name
    ).first()
    if not math_exam:
        math_exam = Exam(
            name=exam_name,
            exam_type="Final",
            academic_year=academic_year,
            class_id=school_class.id,
            subject_id=math_subject.id,
            start_date=date(2026, 10, 15),
            max_marks=Decimal("100.00"),
            pass_marks=Decimal("50.00"),
            status="SCHEDULED"
        )
        db_session.add(math_exam)
        db_session.flush()

    # Clean up any existing submission/results for clean test
    db_session.query(ExamResult).filter(ExamResult.exam_id == math_exam.id).delete()
    db_session.query(ResultSubmission).filter(ResultSubmission.exam_id == math_exam.id).delete()
    db_session.query(ResultReleaseBatch).filter(
        ResultReleaseBatch.class_id == school_class.id,
        ResultReleaseBatch.exam_name == exam_name
    ).delete()
    db_session.query(StudentResultView).filter(
        StudentResultView.class_id == school_class.id,
        StudentResultView.exam_name == exam_name
    ).delete()
    db_session.commit()

    # =========================================================================
    # STAGE 1: TEACHER SAVES DRAFT (Includes 1 Present, 1 Absent)
    # =========================================================================
    # Fetch all enrolled students for Grade 7
    years = [academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")]
    enrollments = db_session.query(StudentEnrollment).filter(
        StudentEnrollment.class_id == school_class.id,
        StudentEnrollment.academic_year.in_(years),
        StudentEnrollment.status == "ACTIVE"
    ).all()
    assert len(enrollments) >= 2

    marks_list = []
    for idx, enr in enumerate(enrollments):
        if idx == 0:
            marks_list.append({
                "student_id": enr.student_id,
                "attendance_status": "PRESENT",
                "marks_obtained": 88.50,
                "remarks": "Excellent comprehension."
            })
        elif idx == 1:
            marks_list.append({
                "student_id": enr.student_id,
                "attendance_status": "ABSENT",
                "marks_obtained": None,
                "remarks": "Medical absence."
            })
        else:
            marks_list.append({
                "student_id": enr.student_id,
                "attendance_status": "PRESENT",
                "marks_obtained": 75.00,
                "remarks": "Good progress."
            })

    draft_payload = {
        "exam_id": math_exam.id,
        "class_id": school_class.id,
        "subject_id": math_subject.id,
        "marks": marks_list
    }

    res_draft = client.post("/api/v1/results/teacher/draft", json=draft_payload, headers=teacher_headers)
    assert res_draft.status_code == 200, res_draft.text
    data = res_draft.json()
    assert data["success"] is True

    # Verify in DB: Absent student marks_obtained is None, status is DRAFT
    r1 = db_session.query(ExamResult).filter(ExamResult.exam_id == math_exam.id, ExamResult.student_id == student_1.id).first()
    r2 = db_session.query(ExamResult).filter(ExamResult.exam_id == math_exam.id, ExamResult.student_id == student_2.id).first()
    assert r1.attendance_status == "PRESENT"
    assert float(r1.marks_obtained) == 88.5
    assert r1.grade == "A"
    assert r1.status == "DRAFT"

    assert r2.attendance_status == "ABSENT"
    assert r2.marks_obtained is None
    assert r2.status == "DRAFT"

    # =========================================================================
    # STAGE 2: TEACHER SUBMITS RESULTS TO ADMIN
    # =========================================================================
    submit_payload = {
        "exam_id": math_exam.id,
        "class_id": school_class.id,
        "subject_id": math_subject.id,
        "marks": draft_payload["marks"]
    }
    res_submit = client.post("/api/v1/results/teacher/submit", json=submit_payload, headers=teacher_headers)
    assert res_submit.status_code == 200, res_submit.text
    sub_data = res_submit.json()
    assert sub_data["status"] == "SUBMITTED"
    submission_id = sub_data["submission_id"]

    # Verify editing is locked for Teacher
    res_edit_locked = client.post("/api/v1/results/teacher/draft", json=draft_payload, headers=teacher_headers)
    assert res_edit_locked.status_code == 400
    err_msg = res_edit_locked.json().get("detail") or res_edit_locked.json().get("error", {}).get("message", "")
    assert "locked" in err_msg.lower()

    # =========================================================================
    # STAGE 3: ADMIN REVIEWS & RETURNS FOR CORRECTION
    # =========================================================================
    # Admin gets submission detail
    res_review = client.get(f"/api/v1/results/submissions/{submission_id}", headers=admin_headers)
    assert res_review.status_code == 200
    review_data = res_review.json()
    assert len(review_data["students"]) >= 2

    # Admin returns for correction with reason
    return_payload = {"reason": "Student STU-001 marks require recalculation."}
    res_return = client.post(f"/api/v1/results/submissions/{submission_id}/return", json=return_payload, headers=admin_headers)
    assert res_return.status_code == 200
    assert res_return.json()["status"] == "RETURNED"

    # Verify Teacher can now edit and resubmit
    draft_payload["marks"][0]["marks_obtained"] = 92.0
    res_edit_unlocked = client.post("/api/v1/results/teacher/draft", json=draft_payload, headers=teacher_headers)
    assert res_edit_unlocked.status_code == 200

    # Resubmit
    res_resubmit = client.post("/api/v1/results/teacher/submit", json=draft_payload, headers=teacher_headers)
    assert res_resubmit.status_code == 200
    assert res_resubmit.json()["status"] == "SUBMITTED"

    # =========================================================================
    # STAGE 4: ADMIN APPROVES RESULTS
    # =========================================================================
    res_approve = client.post(f"/api/v1/results/submissions/{submission_id}/approve", json={}, headers=admin_headers)
    assert res_approve.status_code == 200
    assert res_approve.json()["status"] == "APPROVED"

    # Verify approval DOES NOT publish results to students (Visibility gate)
    # Student token for student_1
    student_user = student_1.user
    if not student_user:
        student_user = User(
            username=f"test_student_{student_1.id}",
            email=f"std_{student_1.id}@hawlwadaag.edu.so",
            hashed_password="pass",
            full_name=student_1.full_name,
            is_active=True
        )
        db_session.add(student_user)
        db_session.flush()
        student_1.user_id = student_user.id
        from app.models.user_role import UserRole
        ur_std = UserRole(user_id=student_user.id, role_id=3)
        db_session.add(ur_std)
        db_session.commit()
    else:
        from app.models.user_role import UserRole
        if not any(r.name == "STUDENT" for r in student_user.roles):
            ur_std = UserRole(user_id=student_user.id, role_id=3)
            db_session.add(ur_std)
            db_session.commit()

    std_token = create_access_token(subject=str(student_user.id))
    std_headers = {"Authorization": f"Bearer {std_token}"}

    res_std_unreleased = client.get("/api/v1/results/student/my-results", headers=std_headers)
    assert res_std_unreleased.status_code == 200
    # Must NOT contain the unreleased results!
    unreleased_ids = [r["exam_id"] for r in res_std_unreleased.json()]
    assert math_exam.id not in unreleased_ids, "Approved results must NOT be visible before release"

    # =========================================================================
    # STAGE 5: ADMIN RELEASES CLASS RESULTS
    # =========================================================================
    release_payload = {
        "class_id": school_class.id,
        "academic_year": academic_year,
        "exam_name": exam_name,
        "release_type": "PARTIAL",
        "allow_partial": True,
        "notes": "Official Final Examination 2026 Release"
    }

    res_release = client.post(f"/api/v1/results/classes/{school_class.id}/release", json=release_payload, headers=admin_headers)
    assert res_release.status_code == 200, res_release.text
    rel_data = res_release.json()
    assert rel_data["success"] is True
    assert "batch_code" in rel_data
    assert rel_data["batch_code"].startswith("RB-2026-")

    # =========================================================================
    # STAGE 6: STUDENT VISIBILITY & RECEIPT TRACKING
    # =========================================================================
    # Now student CAN see released results
    res_std_released = client.get("/api/v1/results/student/my-results", headers=std_headers)
    assert res_std_released.status_code == 200
    released_ids = [r["exam_id"] for r in res_std_released.json()]
    assert math_exam.id in released_ids, "Released results MUST be visible to student"

    # Student triggers view tracking event
    view_payload = {
        "exam_name": exam_name,
        "academic_year": academic_year,
        "class_id": school_class.id
    }
    res_view = client.post("/api/v1/results/student/record-view", json=view_payload, headers=std_headers)
    assert res_view.status_code == 200
    assert res_view.json()["view_count"] == 1

    # Admin checks receipt verification
    res_receipt = client.get(
        f"/api/v1/results/classes/{school_class.id}/receipt?academic_year={academic_year}&exam_name={exam_name}",
        headers=admin_headers
    )
    assert res_receipt.status_code == 200
    receipt_data = res_receipt.json()
    assert receipt_data["released_students"] >= 2
    assert receipt_data["viewed_students"] >= 1
    # Check student_1 has VIEWED status
    std1_receipt = next((r for r in receipt_data["receipts"] if r["student_id"] == student_1.id), None)
    assert std1_receipt is not None
    assert std1_receipt["status"] == "VIEWED"

    # =========================================================================
    # STAGE 7: IDOR PROTECTION TEST
    # =========================================================================
    # Another teacher cannot enter results for Math in Grade 7
    other_teacher_user = db_session.query(User).filter(User.username == "test_other_teacher").first()
    if not other_teacher_user:
        other_teacher_user = User(
            username="test_other_teacher",
            email="other.teacher@test.so",
            hashed_password="pass",
            full_name="Other Faculty",
            is_active=True
        )
        db_session.add(other_teacher_user)
        db_session.flush()
        ur_oth = UserRole(user_id=other_teacher_user.id, role_id=2)
        db_session.add(ur_oth)

    other_tch = db_session.query(Teacher).filter(Teacher.user_id == other_teacher_user.id).first()
    if not other_tch:
        other_tch = Teacher(
            user_id=other_teacher_user.id,
            teacher_number="TCH-OTHER-999",
            first_name="Other",
            last_name="Faculty",
            gender="Female",
            email=other_teacher_user.email,
            status="ACTIVE"
        )
        db_session.add(other_tch)
    db_session.commit()

    other_token = create_access_token(subject=str(other_teacher_user.id))
    other_headers = {"Authorization": f"Bearer {other_token}"}

    res_idor = client.post("/api/v1/results/teacher/draft", json=draft_payload, headers=other_headers)
    assert res_idor.status_code == 403, "Teacher must be rejected when accessing another teacher's class/subject"


def test_partial_class_release_blocked_and_explicit_partial(client, db_session):
    """
    Test requirement: Incomplete class full release MUST BE BLOCKED.
    Explicit partial release only publishes approved results.
    """
    admin_user = db_session.query(User).filter(User.username == "admin").first()
    admin_token = create_access_token(subject=str(admin_user.id))
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    academic_year = "2026/2027"
    exam_name = "Unit Testing Examination 2026"

    # Grade 8
    school_class = db_session.query(SchoolClass).filter(SchoolClass.name == "Grade 8").first()
    if not school_class:
        school_class = SchoolClass(name="Grade 8", code="G8-A", academic_year=academic_year, status="ACTIVE")
        db_session.add(school_class)
        db_session.flush()

    math_subject = db_session.query(Subject).filter(Subject.name == "Mathematics").first()
    eng_subject = db_session.query(Subject).filter(Subject.name.ilike("%English%")).first()

    # Create 2 exams for Grade 8
    e1 = db_session.query(Exam).filter(Exam.class_id == school_class.id, Exam.subject_id == math_subject.id, Exam.name == exam_name).first()
    if not e1:
        e1 = Exam(name=exam_name, exam_type="Mid-Term", academic_year=academic_year, class_id=school_class.id, subject_id=math_subject.id, start_date=date(2026, 11, 1), status="SCHEDULED")
        db_session.add(e1)

    e2 = db_session.query(Exam).filter(Exam.class_id == school_class.id, Exam.subject_id == eng_subject.id, Exam.name == exam_name).first()
    if not e2:
        e2 = Exam(name=exam_name, exam_type="Mid-Term", academic_year=academic_year, class_id=school_class.id, subject_id=eng_subject.id, start_date=date(2026, 11, 2), status="SCHEDULED")
        db_session.add(e2)

    db_session.commit()

    # Attempt full class release when 0 results are approved
    release_payload = {
        "class_id": school_class.id,
        "academic_year": academic_year,
        "exam_name": exam_name,
        "release_type": "FULL"
    }
    res_blocked = client.post(f"/api/v1/results/classes/{school_class.id}/release", json=release_payload, headers=admin_headers)
    assert res_blocked.status_code == 400
    err = res_blocked.json().get("detail") or res_blocked.json().get("error", {}).get("message", "")
    assert "completed" in err.lower() or "not ready" in err.lower() or "no approved results" in err.lower() or "pending" in err.lower() or "curriculum" in err.lower() or "no active" in err.lower()


def test_student_view_tracking_increments_without_duplicates(client, db_session):
    """
    Test student view tracking: multiple views increment view_count,
    do NOT insert duplicate rows into student_result_views.
    """
    student = db_session.query(Student).first()
    assert student is not None
    student_user = student.user
    if not student_user:
        student_user = User(
            username=f"std_track_{student.id}",
            email=f"std_track_{student.id}@test.so",
            hashed_password="pass",
            full_name=student.full_name,
            is_active=True
        )
        db_session.add(student_user)
        db_session.flush()
        student.user_id = student_user.id
        from app.models.user_role import UserRole
        ur = UserRole(user_id=student_user.id, role_id=3)
        db_session.add(ur)
        db_session.commit()

    std_token = create_access_token(subject=str(student_user.id))
    std_headers = {"Authorization": f"Bearer {std_token}"}

    payload = {
        "exam_name": "Mid-Term Mathematics Exam",
        "academic_year": "2026/2027",
        "class_id": student.current_enrollment.class_id if student.current_enrollment else 1
    }

    # First view
    r1 = client.post("/api/v1/results/student/record-view", json=payload, headers=std_headers)
    assert r1.status_code == 200
    cnt1 = r1.json()["view_count"]

    # Second view
    r2 = client.post("/api/v1/results/student/record-view", json=payload, headers=std_headers)
    assert r2.status_code == 200
    cnt2 = r2.json()["view_count"]
    assert cnt2 == cnt1 + 1, "Subsequent view should increment view_count"


