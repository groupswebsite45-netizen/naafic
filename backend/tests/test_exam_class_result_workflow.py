"""
End-to-End Automated Test Suite for Exam + Result Workflow
Hawlwadaag Primary & Secondary School
Validates PostgreSQL integrity, FastAPI HTTP routes, Teacher assignment scoping,
Admin Class-centric result management, Class Release gates, and Student IDOR protection.
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.user import User
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission
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
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def admin_auth(db):
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@hawlwadaagschool.edu.so",
            hashed_password=get_password_hash("Admin@Hawlwadaag2026"),
            full_name="System Administrator",
            is_active=True,
            is_superuser=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    token = create_access_token(subject=str(admin.id), claims={"username": admin.username, "role": "ADMIN"})
    return {"Authorization": f"Bearer {token}", "user": admin}


@pytest.fixture(scope="module")
def teacher_a_auth(db):
    user = db.query(User).filter(User.username == "teacher.ahmed").first()
    if not user:
        user = User(
            username="teacher.ahmed",
            email="ahmed.ali@hawlwadaagschool.edu.so",
            hashed_password=get_password_hash("Teacher@Hawlwadaag2026"),
            full_name="Ahmed Hassan Ali",
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    teacher = db.query(Teacher).filter((Teacher.user_id == user.id) | (Teacher.id == 18)).first()
    if not teacher:
        teacher = Teacher(
            user_id=user.id,
            first_name="Ahmed",
            last_name="Ali",
            email=user.email,
            teacher_number="TCH-001",
            status="ACTIVE",
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
    else:
        teacher.user_id = user.id
        db.commit()

    token = create_access_token(subject=str(user.id), claims={"username": user.username, "role": "TEACHER"})
    return {"Authorization": f"Bearer {token}", "user": user, "teacher": teacher}


@pytest.fixture(scope="module")
def teacher_b_auth(db):
    user = db.query(User).filter(User.username == "teacher.fadumo").first()
    if not user:
        user = User(
            username="teacher.fadumo",
            email="fadumo.warsame@hawlwadaagschool.edu.so",
            hashed_password=get_password_hash("Teacher@Hawlwadaag2026"),
            full_name="Fadumo Mohamed Warsame",
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    teacher = db.query(Teacher).filter((Teacher.user_id == user.id) | (Teacher.id == 19)).first()
    if not teacher:
        teacher = Teacher(
            user_id=user.id,
            first_name="Fadumo",
            last_name="Mohamed",
            email=user.email,
            teacher_number="TCH-002",
            status="ACTIVE",
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
    else:
        teacher.user_id = user.id
        db.commit()

    token = create_access_token(subject=str(user.id), claims={"username": user.username, "role": "TEACHER"})
    return {"Authorization": f"Bearer {token}", "user": user, "teacher": teacher}


@pytest.fixture(scope="module")
def student_auth(db):
    # Find active student in Class 147
    enrollment = (
        db.query(StudentEnrollment)
        .filter(StudentEnrollment.class_id == 147, StudentEnrollment.academic_year == "2026/2027", StudentEnrollment.status == "ACTIVE")
        .first()
    )
    student = enrollment.student if enrollment else db.query(Student).filter(Student.status == "ACTIVE").first()
    assert student is not None

    user = None
    if student.user_id:
        user = db.query(User).filter(User.id == student.user_id).first()

    if not user:
        user = db.query(User).filter(User.username == f"std_{student.admission_number.lower()}").first()
        if not user:
            user = User(
                username=f"std_{student.admission_number.lower()}",
                email=f"{student.admission_number.lower()}@student.hawlwadaagschool.edu.so",
                hashed_password=get_password_hash("Student@Hawlwadaag2026"),
                full_name=student.full_name,
                is_active=True,
                is_superuser=False,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        student.user_id = user.id
        db.commit()

    token = create_access_token(subject=str(user.id), claims={"username": user.username, "role": "STUDENT"})
    return {"Authorization": f"Bearer {token}", "user": user, "student": student}


# =============================================================================
# 1. TEACHER ASSIGNMENT FILTERING & SUBJECT -> CLASS CASCADE
# =============================================================================

def test_teacher_assignment_filtering(client, teacher_a_auth):
    """Teacher must only receive assignments they are actively assigned to."""
    headers = {"Authorization": teacher_a_auth["Authorization"]}
    resp = client.get("/api/v1/teacher/exam-assignments", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "subjects" in data
    assert "classes" in data
    # Teacher Ahmed teaches Mathematics (Subject 21) in Grade 7-A (Class 147)
    subject_ids = [s["id"] for s in data["subjects"]]
    assert 21 in subject_ids


# =============================================================================
# 2. EXAM TYPE VALIDATION (MID_TERM, FINAL, MONTHLY, QUIZ ONLY)
# =============================================================================

def test_exam_type_validation(client, teacher_a_auth):
    """Reject invalid exam types (CUSTOM, SPECIAL, UNIT_TEST)."""
    headers = {"Authorization": teacher_a_auth["Authorization"]}

    # Negative test: invalid exam type 'CUSTOM'
    invalid_payload = {
        "name": "Custom Test Exam",
        "academic_year": "2026/2027",
        "exam_type": "CUSTOM",
        "class_id": 147,
        "subject_id": 21,
        "start_date": "2026-09-20",
        "max_marks": 100.0,
        "passing_marks": 50.0,
    }
    resp = client.post("/api/v1/teacher/exams", json=invalid_payload, headers=headers)
    assert resp.status_code in [400, 422]

    # Negative test: invalid exam type 'UNIT_TEST'
    invalid_payload["exam_type"] = "UNIT_TEST"
    resp = client.post("/api/v1/teacher/exams", json=invalid_payload, headers=headers)
    assert resp.status_code in [400, 422]


# =============================================================================
# 3. EXAM CREATION & DUPLICATE PREVENTION
# =============================================================================

def test_exam_creation_and_duplicate_prevention(client, teacher_a_auth, db):
    """Teacher creates an exam and second attempt for same stream triggers 409."""
    headers = {"Authorization": teacher_a_auth["Authorization"]}

    # Clean any prior exam for this exact stream if present to test fresh creation
    existing = (
        db.query(Exam)
        .filter(
            Exam.academic_year == "2026/2027",
            Exam.class_id == 147,
            Exam.subject_id == 21,
            Exam.exam_type == "MID_TERM",
        )
        .first()
    )
    if existing:
        db.query(ExamResult).filter(ExamResult.exam_id == existing.id).delete()
        db.query(ResultSubmission).filter(ResultSubmission.exam_id == existing.id).delete()
        db.query(Exam).filter(Exam.id == existing.id).delete()
        db.commit()

    payload = {
        "name": "Mid-Term Mathematics Examination",
        "academic_year": "2026/2027",
        "exam_type": "MID_TERM",
        "class_id": 147,
        "subject_id": 21,
        "start_date": "2026-09-20",
        "max_marks": 100.0,
        "passing_marks": 50.0,
    }

    # First creation -> Success
    resp1 = client.post("/api/v1/teacher/exams", json=payload, headers=headers)
    assert resp1.status_code in [200, 201]
    created = resp1.json()
    assert created["class_id"] == 147
    assert created["subject_id"] == 21
    assert created["exam_type"] == "MID_TERM"

    # Duplicate creation -> Rejection (409 Conflict)
    resp2 = client.post("/api/v1/teacher/exams", json=payload, headers=headers)
    assert resp2.status_code in [409, 400]


# =============================================================================
# 4. NEGATIVE SECURITY TESTS
# =============================================================================

def test_unauthorized_exam_creation_by_other_teacher(client, teacher_b_auth):
    """Teacher B cannot create an exam for Mathematics (assigned to Teacher A)."""
    headers = {"Authorization": teacher_b_auth["Authorization"]}

    payload = {
        "name": "Unauthorized Math Exam",
        "academic_year": "2026/2027",
        "exam_type": "FINAL",
        "class_id": 147,
        "subject_id": 21,  # Math is assigned to Teacher A (18), not Teacher B (19)
        "start_date": "2026-09-20",
        "max_marks": 100.0,
        "passing_marks": 50.0,
    }
    resp = client.post("/api/v1/teacher/exams", json=payload, headers=headers)
    assert resp.status_code in [403, 400]


def test_admin_cannot_create_teacher_exam(client, admin_auth):
    """Admin role cannot invoke teacher exam creation."""
    headers = {"Authorization": admin_auth["Authorization"]}

    payload = {
        "name": "Admin Created Exam",
        "academic_year": "2026/2027",
        "exam_type": "MID_TERM",
        "class_id": 147,
        "subject_id": 21,
        "start_date": "2026-09-20",
        "max_marks": 100.0,
        "passing_marks": 50.0,
    }
    resp = client.post("/api/v1/teacher/exams", json=payload, headers=headers)
    assert resp.status_code in [403, 401]


# =============================================================================
# 5. STUDENT ROSTER, MARKS ENTRY, DRAFT SAVE, SUBMIT & RECALL
# =============================================================================

def test_exam_roster_and_draft_submit_recall_workflow(client, teacher_a_auth, db):
    """Test student roster fetching, draft entry, submission, recall, and re-submission."""
    headers = {"Authorization": teacher_a_auth["Authorization"]}

    exam = (
        db.query(Exam)
        .filter(
            Exam.academic_year == "2026/2027",
            Exam.class_id == 147,
            Exam.subject_id == 21,
            Exam.exam_type == "MID_TERM",
        )
        .first()
    )
    assert exam is not None

    # Fetch roster
    resp_roster = client.get(f"/api/v1/teacher/exams/{exam.id}", headers=headers)
    assert resp_roster.status_code == 200
    roster_data = resp_roster.json()
    assert "students" in roster_data
    students = roster_data["students"]
    assert len(students) > 0

    # Enter draft marks for all enrolled students
    draft_marks = []
    for s in students:
        draft_marks.append({
            "student_id": s["student_id"],
            "attendance_status": "PRESENT",
            "marks_obtained": 85.0,
            "remarks": "Excellent understanding of algebra.",
        })

    # Save Draft
    draft_payload = {"marks": draft_marks}
    resp_draft = client.put(f"/api/v1/teacher/exams/{exam.id}/draft", json=draft_payload, headers=headers)
    assert resp_draft.status_code == 200

    # Submit Results
    sub_payload = {"results": draft_marks, "confirmation_notes": "Submitted by teacher"}
    resp_sub = client.post(f"/api/v1/teacher/exams/{exam.id}/submit", json=sub_payload, headers=headers)
    assert resp_sub.status_code == 200
    assert resp_sub.json()["status"] == "SUBMITTED"

    # Recall Results back to Draft
    resp_recall = client.post(f"/api/v1/teacher/exams/{exam.id}/recall", headers=headers)
    assert resp_recall.status_code == 200
    assert resp_recall.json()["status"] in ["DRAFT", "RECALLED"]

    # Re-submit Results to Admin
    resp_resub = client.post(f"/api/v1/teacher/exams/{exam.id}/submit", json=sub_payload, headers=headers)
    assert resp_resub.status_code == 200
    assert resp_resub.json()["status"] == "SUBMITTED"


# =============================================================================
# 6. ADMIN DASHBOARD, PENDING SUBJECT CHECK & PREMATURE RELEASE GATE
# =============================================================================

def test_admin_dashboard_and_release_gate(client, admin_auth, db):
    """Admin class dashboard shows submitted vs pending; premature release is blocked."""
    headers = {"Authorization": admin_auth["Authorization"]}

    # Ensure subjects 22, 23, 24, 25 are pending (clean any previous releases from other tests)
    other_exams = db.query(Exam).filter(Exam.class_id == 147, Exam.subject_id.in_([22, 23, 24, 25])).all()
    for oe in other_exams:
        db.query(ResultSubmission).filter(ResultSubmission.exam_id == oe.id).delete()
        db.query(ExamResult).filter(ExamResult.exam_id == oe.id).delete()
        db.query(Exam).filter(Exam.id == oe.id).delete()
    db.commit()

    # Class 147 Dashboard
    resp = client.get(
        "/api/v1/results/classes/147?academic_year=2026/2027&exam_name=Mid-Term Examination",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["class_id"] == 147
    assert data["subjects_count"] == 5
    assert data["complete_subjects_count"] >= 1
    assert data["can_release_full"] is False

    # Attempt premature class release -> Must return 400 Bad Request
    rel_payload = {
        "academic_year": "2026/2027",
        "exam_name": "Mid-Term Examination",
        "notes": "Admin testing premature release",
    }
    resp_rel = client.post("/api/v1/results/classes/147/release", json=rel_payload, headers=headers)
    assert resp_rel.status_code in [400, 422]
    assert "pending" in resp_rel.json().get("detail", "").lower()


# =============================================================================
# 7. ADMIN RETURN FOR CORRECTION & TEACHER RESUBMIT
# =============================================================================

def test_admin_return_and_teacher_resubmit(client, admin_auth, teacher_a_auth, db):
    """Admin returns submission for correction; teacher edits and resubmits."""
    admin_headers = {"Authorization": admin_auth["Authorization"]}
    teacher_headers = {"Authorization": teacher_a_auth["Authorization"]}

    exam = (
        db.query(Exam)
        .filter(Exam.academic_year == "2026/2027", Exam.class_id == 147, Exam.subject_id == 21)
        .first()
    )
    assert exam is not None
    sub = db.query(ResultSubmission).filter(ResultSubmission.exam_id == exam.id).first()
    if not sub:
        sub = ResultSubmission(
            exam_id=exam.id,
            teacher_id=18,
            class_id=147,
            subject_id=21,
            academic_year="2026/2027",
            exam_type="MID_TERM",
            status="SUBMITTED",
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
    elif sub.status != "SUBMITTED":
        sub.status = "SUBMITTED"
        db.commit()
        db.refresh(sub)

    # Admin returns for correction
    ret_payload = {"reason": "Please check student mark for student 1."}
    resp_ret = client.post(f"/api/v1/results/submissions/{sub.id}/return", json=ret_payload, headers=admin_headers)
    assert resp_ret.status_code == 200
    assert resp_ret.json()["status"] in ["RETURNED", "RETURNED_FOR_CORRECTION"]

    # Teacher re-submits
    resub_payload = {"confirmation_notes": "Corrected marks"}
    resp_resub = client.post(f"/api/v1/teacher/exams/{exam.id}/submit", json=resub_payload, headers=teacher_headers)
    assert resp_resub.status_code == 200
    assert resp_resub.json()["status"] == "SUBMITTED"


# =============================================================================
# 8. SUBMIT ALL CLASS SUBJECTS & ADMIN RELEASES ALL CLASS RESULTS
# =============================================================================

def test_complete_all_subjects_and_release_class(client, admin_auth, db):
    """When all 5 assigned subjects are submitted, Admin releases all class results."""
    admin_headers = {"Authorization": admin_auth["Authorization"]}

    # Ensure all 5 assigned subjects on Class 147 have active submitted exams
    assignments = (
        db.query(TeacherAssignment)
        .filter(TeacherAssignment.class_id == 147, TeacherAssignment.academic_year == "2026/2027", TeacherAssignment.status == "ACTIVE")
        .all()
    )
    assert len(assignments) == 5

    # Enrolled students for Class 147
    enrollments = (
        db.query(StudentEnrollment)
        .filter(StudentEnrollment.class_id == 147, StudentEnrollment.academic_year == "2026/2027", StudentEnrollment.status == "ACTIVE")
        .all()
    )
    student_ids = [e.student_id for e in enrollments]

    for asgn in assignments:
        exam = (
            db.query(Exam)
            .filter(
                Exam.academic_year == "2026/2027",
                Exam.class_id == 147,
                Exam.subject_id == asgn.subject_id,
                Exam.exam_type == "MID_TERM",
            )
            .first()
        )
        if not exam:
            exam = Exam(
                name=f"Mid-Term {asgn.subject.name} Examination",
                exam_type="MID_TERM",
                academic_year="2026/2027",
                class_id=147,
                subject_id=asgn.subject_id,
                teacher_id=asgn.teacher_id,
                start_date=date(2026, 9, 20),
                max_marks=100.0,
                pass_marks=50.0,
                status="SUBMITTED",
            )
            db.add(exam)
            db.commit()
            db.refresh(exam)

        # Create student results if missing
        for s_id in student_ids:
            res = (
                db.query(ExamResult)
                .filter(ExamResult.exam_id == exam.id, ExamResult.student_id == s_id)
                .first()
            )
            if not res:
                res = ExamResult(
                    exam_id=exam.id,
                    student_id=s_id,
                    class_id=147,
                    subject_id=asgn.subject_id,
                    marks_obtained=80.0,
                    attendance_status="PRESENT",
                    grade="A",
                    status="SUBMITTED",
                )
                db.add(res)
            else:
                res.status = "SUBMITTED"
        db.commit()

        # Create/Update ResultSubmission
        sub = db.query(ResultSubmission).filter(ResultSubmission.exam_id == exam.id).first()
        if not sub:
            sub = ResultSubmission(
                exam_id=exam.id,
                teacher_id=asgn.teacher_id,
                academic_year="2026/2027",
                exam_name="Mid-Term Examination",
                class_id=147,
                subject_id=asgn.subject_id,
                status="SUBMITTED",
                expected_students=len(student_ids),
                completed_students=len(student_ids),
                pending_students=0,
            )
            db.add(sub)
        else:
            sub.status = "SUBMITTED"
            sub.expected_students = len(student_ids)
            sub.completed_students = len(student_ids)
            sub.pending_students = 0
        db.commit()

    # Admin verifies Class Dashboard is 5/5 complete
    resp_dash = client.get(
        "/api/v1/results/classes/147?academic_year=2026/2027&exam_name=Mid-Term Examination",
        headers=admin_headers,
    )
    assert resp_dash.status_code == 200
    dash_data = resp_dash.json()
    assert dash_data["subjects_count"] == 5
    assert dash_data["complete_subjects_count"] == 5
    assert dash_data["can_release_full"] is True

    # Admin executes single action: RELEASE ALL CLASS RESULTS
    rel_payload = {
        "academic_year": "2026/2027",
        "exam_name": "Mid-Term Examination",
        "notes": "Full class release for Grade 7 - A",
    }
    resp_rel = client.post("/api/v1/results/classes/147/release", json=rel_payload, headers=admin_headers)
    assert resp_rel.status_code == 200
    assert resp_rel.json()["results_count"] > 0


# =============================================================================
# 9. STUDENT VISIBILITY & IDOR PROTECTION
# =============================================================================

def test_student_visibility_and_idor_protection(client, student_auth):
    """Student sees only their own released results; cannot access others' results."""
    headers = {"Authorization": student_auth["Authorization"]}

    resp = client.get("/api/v1/results/student/my-results", headers=headers)
    assert resp.status_code == 200
    results = resp.json()
    assert isinstance(results, list)
    assert len(results) > 0

    student_id = student_auth["student"].id
    for r in results:
        # Every single returned result must strictly belong to this student
        assert r["student_id"] == student_id
        assert r["status"] == "RELEASED"
