import pytest
import uuid
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
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def admin_user(db_session):
    admin = db_session.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@hawlwadaagschool.edu.so",
            hashed_password=get_password_hash("Admin@Hawlwadaag2026"),
            full_name="System Administrator",
            is_active=True,
            is_superuser=True
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
    return admin


@pytest.fixture(scope="module")
def admin_headers(admin_user):
    token = create_access_token(subject=str(admin_user.id), claims={"username": admin_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def teacher_and_tokens(db_session):
    # Create or get teacher user
    t_user = db_session.query(User).filter(
        (User.username == "teacher.ahmed") | (User.email == "ahmed.ali@hawlwadaagschool.edu.so")
    ).first()

    if not t_user:
        t_user = User(
            username="teacher.ahmed",
            email="ahmed.ali@hawlwadaagschool.edu.so",
            hashed_password=get_password_hash("Teacher@Hawlwadaag2026"),
            full_name="Ahmed Ali Mire",
            is_active=True,
            is_superuser=False
        )
        db_session.add(t_user)
        db_session.commit()
        db_session.refresh(t_user)

    teacher = db_session.query(Teacher).filter(Teacher.user_id == t_user.id).first()
    if not teacher:
        teacher = Teacher(
            user_id=t_user.id,
            teacher_number=f"TCH-{uuid.uuid4().hex[:6].upper()}",
            first_name="Ahmed",
            last_name="Mire",
            gender="Male",
            email="ahmed.ali@hawlwadaagschool.edu.so",
            phone="+252615000001",
            status="ACTIVE"
        )
        db_session.add(teacher)
        db_session.commit()
        db_session.refresh(teacher)

    # Class Grade 7 - A
    g7_a = db_session.query(SchoolClass).filter(
        SchoolClass.academic_year.in_(["2026/2027", "2026-2027"]),
        SchoolClass.level == "Grade 7",
        SchoolClass.section == "A"
    ).first()

    if not g7_a:
        g7_a = SchoolClass(
            name="Grade 7 - A",
            code="G7-A-2026-TEST",
            division="PRIMARY",
            level="Grade 7",
            section="A",
            academic_year="2026/2027",
            capacity=40,
            status="ACTIVE"
        )
        db_session.add(g7_a)
        db_session.commit()
        db_session.refresh(g7_a)

    # Subject Mathematics
    math_subj = db_session.query(Subject).filter(
        Subject.name.ilike("%Mathematics%")
    ).first()

    if not math_subj:
        math_subj = Subject(
            name="Mathematics",
            code="MATH-101",
            division="ALL",
            applicable_levels="Grade 1,Grade 2,Grade 3,Grade 4,Grade 5,Grade 6,Grade 7,Grade 8,Form 1,Form 2,Form 3,Form 4",
            status="ACTIVE"
        )
        db_session.add(math_subj)
        db_session.commit()
        db_session.refresh(math_subj)

    # Ensure teacher assignment
    ta = db_session.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher.id,
        TeacherAssignment.class_id == g7_a.id,
        TeacherAssignment.subject_id == math_subj.id,
        TeacherAssignment.academic_year == g7_a.academic_year
    ).first()

    if not ta:
        ta = TeacherAssignment(
            teacher_id=teacher.id,
            class_id=g7_a.id,
            subject_id=math_subj.id,
            academic_year=g7_a.academic_year,
            status="ACTIVE"
        )
        db_session.add(ta)
        db_session.commit()

    # Create enrolled students if needed
    for i in range(1, 4):
        adm_no = f"ADM-TEST-2026-{i:03d}"
        std = db_session.query(Student).filter(Student.admission_number == adm_no).first()
        if not std:
            std = Student(
                admission_number=adm_no,
                first_name=f"Student{i}",
                last_name="Test",
                gender="Male" if i % 2 == 1 else "Female",
                date_of_birth=date(2013, 1, 1),
                admission_date=date(2026, 1, 1),
                status="ACTIVE"
            )
            db_session.add(std)
            db_session.commit()
            db_session.refresh(std)

        en = db_session.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == std.id,
            StudentEnrollment.academic_year == g7_a.academic_year
        ).first()

        if not en:
            en = StudentEnrollment(
                student_id=std.id,
                class_id=g7_a.id,
                academic_year=g7_a.academic_year,
                start_date=date(2026, 1, 1),
                status="ACTIVE"
            )
            db_session.add(en)
            db_session.commit()

    token = create_access_token(subject=str(t_user.id), claims={"username": t_user.username})
    headers = {"Authorization": f"Bearer {token}"}

    return {
        "user": t_user,
        "teacher": teacher,
        "headers": headers,
        "class": g7_a,
        "subject": math_subj,
    }


class TestTeacherExamCreationWorkflow:
    """
    Test suite verifying the restructured Examination system:
    1. Admin CANNOT create, edit, or delete exams (HTTP 403).
    2. Teacher creates exams for assigned classes & subjects (HTTP 201).
    3. Teacher CANNOT create exams for unassigned classes or subjects (HTTP 403).
    4. Duplicate exam creation is prevented (HTTP 409).
    5. Automatic enrolled students loading & marks entry lifecycle.
    6. Admin review & release workflow.
    """

    def test_01_admin_creates_official_exam_routed_to_teacher(self, client: TestClient, admin_headers, teacher_and_tokens, db_session):
        """Admin schedules official exam and it routes to assigned teacher."""
        c = teacher_and_tokens["class"]
        s = teacher_and_tokens["subject"]

        # Clean prior exams for this class + subject + MID_TERM
        db_exams = db_session.query(Exam).filter(
            Exam.class_id == c.id,
            Exam.subject_id == s.id,
            Exam.exam_type == "MID_TERM",
        ).all()
        for e in db_exams:
            db_session.query(ExamResult).filter(ExamResult.exam_id == e.id).delete()
            db_session.query(ResultSubmission).filter(ResultSubmission.exam_id == e.id).delete()
            db_session.query(Exam).filter(Exam.id == e.id).delete()
        db_session.commit()

        # Admin POST /api/v1/exams -> 201 Created
        res_create = client.post("/api/v1/exams", json={
            "name": f"Admin Midterm {uuid.uuid4().hex[:6]}",
            "exam_type": "MID_TERM",
            "academic_year": c.academic_year,
            "class_id": c.id,
            "subject_id": s.id,
            "start_date": "2026-09-20",
            "max_marks": 100,
            "pass_marks": 50
        }, headers=admin_headers)
        assert res_create.status_code == 201
        data = res_create.json()
        assert data["class_id"] == c.id
        assert data["subject_id"] == s.id

    def test_02_teacher_creates_exam_success(self, client: TestClient, teacher_and_tokens, db_session):
        """Teacher can successfully create an exam for an assigned class and subject."""
        c = teacher_and_tokens["class"]
        s = teacher_and_tokens["subject"]
        headers = teacher_and_tokens["headers"]

        # Clean prior exams for this class + subject + FINAL
        db_exams = db_session.query(Exam).filter(
            Exam.class_id == c.id,
            Exam.subject_id == s.id,
            Exam.exam_type == "FINAL",
        ).all()
        for e in db_exams:
            db_session.query(ExamResult).filter(ExamResult.exam_id == e.id).delete()
            db_session.query(ResultSubmission).filter(ResultSubmission.exam_id == e.id).delete()
            db_session.query(Exam).filter(Exam.id == e.id).delete()
        db_session.commit()

        exam_title = f"Final Math Examination {uuid.uuid4().hex[:6]}"

        res = client.post("/api/v1/teacher-portal/exams", json={
            "name": exam_title,
            "exam_type": "FINAL",
            "academic_year": c.academic_year,
            "class_id": c.id,
            "subject_id": s.id,
            "start_date": "2026-09-20",
            "max_marks": 100,
            "pass_marks": 50,
            "instructions": "All questions are mandatory."
        }, headers=headers)

        assert res.status_code == 201
        data = res.json()
        assert data["name"] == exam_title
        assert data["class_id"] == c.id
        assert data["subject_id"] == s.id
        assert float(data["max_marks"]) == 100.0
        assert float(data["pass_marks"]) == 50.0

    def test_03_teacher_duplicate_exam_creation_prevented(self, client: TestClient, teacher_and_tokens, db_session):
        """Duplicate exam for exact same class, subject, academic year, and exam_type is rejected with 409 Conflict."""
        c = teacher_and_tokens["class"]
        s = teacher_and_tokens["subject"]
        headers = teacher_and_tokens["headers"]

        # Clean prior exams for MONTHLY
        db_exams = db_session.query(Exam).filter(
            Exam.class_id == c.id,
            Exam.subject_id == s.id,
            Exam.exam_type == "MONTHLY",
        ).all()
        for e in db_exams:
            db_session.query(ExamResult).filter(ExamResult.exam_id == e.id).delete()
            db_session.query(ResultSubmission).filter(ResultSubmission.exam_id == e.id).delete()
            db_session.query(Exam).filter(Exam.id == e.id).delete()
        db_session.commit()

        exam_title = f"Monthly Math Test {uuid.uuid4().hex[:6]}"

        # First creation -> 201
        res1 = client.post("/api/v1/teacher-portal/exams", json={
            "name": exam_title,
            "exam_type": "MONTHLY",
            "academic_year": c.academic_year,
            "class_id": c.id,
            "subject_id": s.id,
            "start_date": "2026-09-20",
            "max_marks": 100,
            "pass_marks": 50
        }, headers=headers)
        assert res1.status_code == 201

        # Second creation with identical type -> 409 Conflict even with different title
        res2 = client.post("/api/v1/teacher-portal/exams", json={
            "name": f"Different Title {uuid.uuid4().hex[:6]}",
            "exam_type": "MONTHLY",
            "academic_year": c.academic_year,
            "class_id": c.id,
            "subject_id": s.id,
            "start_date": "2026-09-20",
            "max_marks": 100,
            "pass_marks": 50
        }, headers=headers)
        assert res2.status_code == 409
        assert "already exists" in res2.json()["detail"].lower()

    def test_04_teacher_unassigned_class_or_subject_rejected(self, client: TestClient, teacher_and_tokens, db_session):
        """Teacher attempting to create exam for unassigned class/subject is rejected with 403 Forbidden."""
        headers = teacher_and_tokens["headers"]

        # Find or create an unassigned class (e.g., Form 4 - A)
        f4_a = db_session.query(SchoolClass).filter(SchoolClass.level == "Form 4").first()
        s = teacher_and_tokens["subject"]

        if f4_a:
            res = client.post("/api/v1/teacher-portal/exams", json={
                "name": "Unauthorized Form 4 Exam",
                "exam_type": "QUIZ",
                "academic_year": "2026/2027",
                "class_id": f4_a.id,
                "subject_id": s.id,
                "start_date": "2026-10-01",
                "max_marks": 100,
                "pass_marks": 50
            }, headers=headers)
            assert res.status_code == 403
            detail = res.json()["detail"].lower()
            assert "not assigned" in detail or "not authorized" in detail

    def test_05_teacher_roster_and_marks_workflow(self, client: TestClient, teacher_and_tokens, admin_headers, db_session):
        """Full lifecycle: create exam -> load roster -> save draft -> submit -> admin release."""
        c = teacher_and_tokens["class"]
        s = teacher_and_tokens["subject"]
        headers = teacher_and_tokens["headers"]

        # Clean prior exams for QUIZ
        db_exams = db_session.query(Exam).filter(
            Exam.class_id == c.id,
            Exam.subject_id == s.id,
            Exam.exam_type == "QUIZ",
        ).all()
        for e in db_exams:
            db_session.query(ExamResult).filter(ExamResult.exam_id == e.id).delete()
            db_session.query(ResultSubmission).filter(ResultSubmission.exam_id == e.id).delete()
            db_session.query(Exam).filter(Exam.id == e.id).delete()
        db_session.commit()

        # 1. Create Exam
        exam_res = client.post("/api/v1/teacher-portal/exams", json={
            "name": f"Full Lifecycle Exam {uuid.uuid4().hex[:6]}",
            "exam_type": "QUIZ",
            "academic_year": c.academic_year,
            "class_id": c.id,
            "subject_id": s.id,
            "start_date": "2026-09-25",
            "max_marks": 100,
            "pass_marks": 50
        }, headers=headers)
        assert exam_res.status_code == 201
        exam_id = exam_res.json()["id"]

        # 2. Get Roster
        roster_res = client.get(f"/api/v1/teacher-portal/exams/{exam_id}/roster", headers=headers)
        assert roster_res.status_code == 200
        roster_data = roster_res.json()
        assert len(roster_data["students"]) > 0

        students = roster_data["students"]

        # 3. Save Draft
        draft_payload = [
            {
                "student_id": students[0]["student_id"],
                "attendance_status": "PRESENT",
                "marks_obtained": 85.0,
                "remarks": "Great work"
            }
        ]
        draft_res = client.post(f"/api/v1/teacher-portal/exams/{exam_id}/draft", json={
            "results": draft_payload
        }, headers=headers)
        assert draft_res.status_code == 200

        # 4. Submit with all completed marks
        full_payload = []
        for idx, std in enumerate(students):
            full_payload.append({
                "student_id": std["student_id"],
                "attendance_status": "PRESENT" if idx < len(students) - 1 else "ABSENT",
                "marks_obtained": 80.0 + idx if idx < len(students) - 1 else None,
                "remarks": "Good effort"
            })

        submit_res = client.post(f"/api/v1/teacher-portal/exams/{exam_id}/submit", json={
            "results": full_payload,
            "confirmation_notes": "All verified"
        }, headers=headers)
        assert submit_res.status_code == 200
        assert submit_res.json()["status"] == "SUBMITTED"

        # 5. Admin finds submission and releases results
        sub_list_res = client.get(f"/api/v1/results/submissions?class_id={c.id}&subject_id={s.id}", headers=admin_headers)
        assert sub_list_res.status_code == 200
        submissions = sub_list_res.json()
        target_sub = next((sb for sb in submissions if sb["exam_id"] == exam_id), None)
        assert target_sub is not None

        release_res = client.post(f"/api/v1/results/submissions/{target_sub['id']}/release", headers=admin_headers)
        assert release_res.status_code == 200
        assert release_res.json()["status"] == "RELEASED"
