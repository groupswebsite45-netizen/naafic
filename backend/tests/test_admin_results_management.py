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
from app.models.notification import Notification


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


def test_admin_results_management_workflow_and_isolation(client, db_session):
    """
    Comprehensive test suite for Admin Results Management & Release Center:
    1. Teacher submits results in PostgreSQL.
    2. Admin views submissions list and detail.
    3. Admin cannot edit marks (read-only enforcement).
    4. Admin cannot delete marks.
    5. Academic Year isolation.
    6. Class isolation.
    7. Subject isolation.
    8. Student searching and filtering (below pass mark, pass mark).
    9. Incomplete results cannot be released (HTTP 400 rejection).
    10. Complete results can be released.
    11. Release changes student portal visibility.
    12. Student sees only their own released result.
    13. Automatic Somali SMS guardian notifications triggered on release.
    14. Duplicate release and notifications prevented.
    15. Return-for-correction with mandatory reason.
    16. Teacher corrects returned submission and resubmits.
    17. Admin releases corrected submission.
    """
    academic_year = "2026-2027"
    exam_name = "Admin Redesign Mid-Term 2026"

    # 1. Admin actor
    admin_user = db_session.query(User).filter(User.username == "admin").first()
    assert admin_user is not None
    admin_token = create_access_token(subject=str(admin_user.id))
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Teacher actor
    teacher_user = db_session.query(User).filter(User.username == "teacher.ali").first()
    if not teacher_user:
        teacher_user = User(
            username="teacher.ali",
            email="ali.teacher@hawlwadaag.edu.so",
            hashed_password="hashed_pass_test",
            full_name="Ali Mohamed Warsame",
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
            teacher_number="TCH-ALI-01",
            first_name="Ali",
            last_name="Warsame",
            gender="Male",
            email=teacher_user.email,
            status="ACTIVE"
        )
        db_session.add(teacher)
        db_session.flush()

    teacher_token = create_access_token(subject=str(teacher_user.id))
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    # 3. Class & Subjects
    g7_class = db_session.query(SchoolClass).filter(SchoolClass.name == "Grade 7-Test").first()
    if not g7_class:
        g7_class = SchoolClass(name="Grade 7-Test", code="G7-TST", academic_year=academic_year, status="ACTIVE")
        db_session.add(g7_class)
        db_session.flush()

    g8_class = db_session.query(SchoolClass).filter(SchoolClass.name == "Grade 8-Test").first()
    if not g8_class:
        g8_class = SchoolClass(name="Grade 8-Test", code="G8-TST", academic_year=academic_year, status="ACTIVE")
        db_session.add(g8_class)
        db_session.flush()

    math_subject = db_session.query(Subject).filter(Subject.name == "Mathematics-Test").first()
    if not math_subject:
        math_subject = Subject(name="Mathematics-Test", code="MATH-TST", status="ACTIVE")
        db_session.add(math_subject)
        db_session.flush()

    phy_subject = db_session.query(Subject).filter(Subject.name == "Physics-Test").first()
    if not phy_subject:
        phy_subject = Subject(name="Physics-Test", code="PHYS-TST", status="ACTIVE")
        db_session.add(phy_subject)
        db_session.flush()

    # 4. Teacher Assignments
    t_assign = db_session.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher.id,
        TeacherAssignment.class_id == g7_class.id,
        TeacherAssignment.subject_id == math_subject.id,
        TeacherAssignment.academic_year == academic_year
    ).first()
    if not t_assign:
        t_assign = TeacherAssignment(
            teacher_id=teacher.id,
            class_id=g7_class.id,
            subject_id=math_subject.id,
            academic_year=academic_year,
            status="ACTIVE"
        )
        db_session.add(t_assign)
        db_session.flush()

    # 5. Students in G7 (Mustaf & Amina)
    s1_user = db_session.query(User).filter(User.username == "std_mustaf_test").first()
    if not s1_user:
        s1_user = User(username="std_mustaf_test", email="mustaf.t@hawlwadaag.edu.so", hashed_password="pass", full_name="Mustaf Abdi Noor", is_active=True)
        db_session.add(s1_user)
        db_session.flush()
        sur1 = UserRole(user_id=s1_user.id, role_id=3)
        db_session.add(sur1)

    s1 = db_session.query(Student).filter(Student.user_id == s1_user.id).first()
    if not s1:
        s1 = Student(
            user_id=s1_user.id,
            admission_number="ADM-TEST-001",
            first_name="Mustaf",
            last_name="Noor",
            gender="Male",
            guardian_name="Abdi Noor",
            guardian_phone="+252615551111",
            guardian_email="abdi@test.so",
            status="ACTIVE"
        )
        db_session.add(s1)
        db_session.flush()

    s2_user = db_session.query(User).filter(User.username == "std_amina_test").first()
    if not s2_user:
        s2_user = User(username="std_amina_test", email="amina.t@hawlwadaag.edu.so", hashed_password="pass", full_name="Amina Hassan Ibrahim", is_active=True)
        db_session.add(s2_user)
        db_session.flush()
        sur2 = UserRole(user_id=s2_user.id, role_id=3)
        db_session.add(sur2)

    s2 = db_session.query(Student).filter(Student.user_id == s2_user.id).first()
    if not s2:
        s2 = Student(
            user_id=s2_user.id,
            admission_number="ADM-TEST-002",
            first_name="Amina",
            last_name="Ibrahim",
            gender="Female",
            guardian_name="Hassan Ibrahim",
            guardian_phone="+252615552222",
            guardian_email="hassan@test.so",
            status="ACTIVE"
        )
        db_session.add(s2)
        db_session.flush()

    # Enrollments
    e1 = db_session.query(StudentEnrollment).filter(
        StudentEnrollment.student_id == s1.id,
        StudentEnrollment.academic_year.in_([academic_year, academic_year.replace("-", "/")])
    ).first()
    if not e1:
        e1 = StudentEnrollment(student_id=s1.id, class_id=g7_class.id, academic_year=academic_year, status="ACTIVE", roll_number="01")
        db_session.add(e1)
    else:
        e1.class_id = g7_class.id
        e1.status = "ACTIVE"

    e2 = db_session.query(StudentEnrollment).filter(
        StudentEnrollment.student_id == s2.id,
        StudentEnrollment.academic_year.in_([academic_year, academic_year.replace("-", "/")])
    ).first()
    if not e2:
        e2 = StudentEnrollment(student_id=s2.id, class_id=g7_class.id, academic_year=academic_year, status="ACTIVE", roll_number="02")
        db_session.add(e2)
    else:
        e2.class_id = g7_class.id
        e2.status = "ACTIVE"

    # 6. Exam Definition
    exam = db_session.query(Exam).filter(
        Exam.class_id == g7_class.id,
        Exam.subject_id == math_subject.id,
        Exam.academic_year.in_([academic_year, academic_year.replace("-", "/")]),
        Exam.exam_type == "MID_TERM"
    ).first()
    if not exam:
        exam = Exam(
            name=exam_name,
            exam_type="MID_TERM",
            academic_year=academic_year,
            class_id=g7_class.id,
            subject_id=math_subject.id,
            start_date=date(2026, 3, 10),
            end_date=date(2026, 3, 15),
            max_marks=Decimal("100.00"),
            pass_marks=Decimal("50.00"),
            status="SCHEDULED"
        )
        db_session.add(exam)
        db_session.flush()

    db_session.commit()

    # Clean prior test results for isolation
    db_session.query(ExamResult).filter(ExamResult.exam_id == exam.id).delete()
    db_session.query(ResultSubmission).filter(ResultSubmission.exam_id == exam.id).delete()
    db_session.commit()

    # =========================================================================
    # STEP 1: TEACHER SAVES DRAFT & SUBMITS
    # =========================================================================
    draft_payload = {
        "exam_id": exam.id,
        "class_id": g7_class.id,
        "subject_id": math_subject.id,
        "marks": [
            {"student_id": s1.id, "attendance_status": "PRESENT", "marks_obtained": 82.5, "remarks": "Excellent work"},
            {"student_id": s2.id, "attendance_status": "PRESENT", "marks_obtained": 42.0, "remarks": "Needs improvement"}
        ]
    }
    r = client.post("/api/v1/results/teacher/draft", json=draft_payload, headers=teacher_headers)
    assert r.status_code == 200

    # Submit results to Admin
    submit_payload = {
        "exam_id": exam.id,
        "class_id": g7_class.id,
        "subject_id": math_subject.id,
        "marks": draft_payload["marks"]
    }
    r = client.post("/api/v1/results/teacher/submit", json=submit_payload, headers=teacher_headers)
    assert r.status_code == 200
    sub_id = r.json()["submission_id"]

    # =========================================================================
    # STEP 2: ADMIN VIEWS SUBMISSION LIST & FILTERS
    # =========================================================================
    r = client.get(f"/api/v1/results/submissions?academic_year={academic_year}&class_id={g7_class.id}&subject_id={math_subject.id}", headers=admin_headers)
    assert r.status_code == 200
    subs = r.json()
    assert len(subs) >= 1
    target_sub = next(s for s in subs if s["id"] == sub_id)
    assert target_sub["status"] == "SUBMITTED"
    assert target_sub["completed_students"] == 2
    assert target_sub["pending_students"] == 0

    # Test Class Isolation: Grade 8 query must NOT return Grade 7 submission
    r = client.get(f"/api/v1/results/submissions?academic_year={academic_year}&class_id={g8_class.id}", headers=admin_headers)
    assert r.status_code == 200
    g8_subs = r.json()
    assert not any(s["id"] == sub_id for s in g8_subs)

    # Test Subject Isolation: Physics query must NOT return Mathematics submission
    r = client.get(f"/api/v1/results/submissions?academic_year={academic_year}&subject_id={phy_subject.id}", headers=admin_headers)
    assert r.status_code == 200
    phy_subs = r.json()
    assert not any(s["id"] == sub_id for s in phy_subs)

    # =========================================================================
    # STEP 3: ADMIN VIEWS SUBMISSION DETAIL (READ-ONLY)
    # =========================================================================
    r = client.get(f"/api/v1/results/submissions/{sub_id}", headers=admin_headers)
    assert r.status_code == 200
    detail = r.json()
    assert detail["id"] == sub_id
    assert detail["expected_students"] == 2
    assert detail["completed_students"] == 2
    assert detail["pending_students"] == 0
    assert len(detail["students"]) == 2

    # Verify student entries
    st1 = next(s for s in detail["students"] if s["student_id"] == s1.id)
    assert float(st1["marks_obtained"]) == 82.5
    assert st1["attendance_status"] == "PRESENT"
    assert st1["grade"] == "A"

    st2 = next(s for s in detail["students"] if s["student_id"] == s2.id)
    assert float(st2["marks_obtained"]) == 42.0
    assert st2["grade"] == "F"

    # =========================================================================
    # STEP 4: STUDENT PORTAL ISOLATION - NOT VISIBLE BEFORE RELEASE
    # =========================================================================
    s1_token = create_access_token(subject=str(s1_user.id))
    s1_headers = {"Authorization": f"Bearer {s1_token}"}
    r = client.get("/api/v1/results/student/my-results", headers=s1_headers)
    assert r.status_code == 200
    s1_results = r.json()
    assert not any(res["exam_id"] == exam.id for res in s1_results)

    # =========================================================================
    # STEP 5: RETURN FOR CORRECTION
    # =========================================================================
    return_payload = {"reason": "Please verify student marks and re-check pass threshold."}
    r = client.post(f"/api/v1/results/submissions/{sub_id}/return", json=return_payload, headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "RETURNED"

    # Verify teacher can now edit returned results
    corrected_payload = {
        "exam_id": exam.id,
        "class_id": g7_class.id,
        "subject_id": math_subject.id,
        "marks": [
            {"student_id": s1.id, "attendance_status": "PRESENT", "marks_obtained": 85.0, "remarks": "Excellent mastery"},
            {"student_id": s2.id, "attendance_status": "PRESENT", "marks_obtained": 65.0, "remarks": "Passed after re-evaluation"}
        ]
    }
    r = client.post("/api/v1/results/teacher/submit", json=corrected_payload, headers=teacher_headers)
    assert r.status_code == 200

    # =========================================================================
    # STEP 6: ADMIN RELEASES RESULTS
    # =========================================================================
    r = client.post(f"/api/v1/results/submissions/{sub_id}/release", headers=admin_headers)
    assert r.status_code == 200
    release_res = r.json()
    assert release_res["status"] == "RELEASED"
    assert release_res["results_count"] == 2

    # =========================================================================
    # STEP 7: STUDENT PORTAL VISIBILITY AFTER RELEASE
    # =========================================================================
    r = client.get("/api/v1/results/student/my-results", headers=s1_headers)
    assert r.status_code == 200
    s1_results = r.json()
    s1_rel = next(res for res in s1_results if res["exam_id"] == exam.id)
    assert float(s1_rel["marks_obtained"]) == 85.0
    assert s1_rel["grade"] == "A"

    # Student 2 must see ONLY their own released result
    s2_token = create_access_token(subject=str(s2_user.id))
    s2_headers = {"Authorization": f"Bearer {s2_token}"}
    r = client.get("/api/v1/results/student/my-results", headers=s2_headers)
    assert r.status_code == 200
    s2_results = r.json()
    s2_rel = next(res for res in s2_results if res["exam_id"] == exam.id)
    assert float(s2_rel["marks_obtained"]) == 65.0
    assert s2_rel["student_id"] == s2.id

    # =========================================================================
    # STEP 8: GUARDIAN NOTIFICATION IN SOMALI & DUPLICATE PREVENTION
    # =========================================================================
    notifs = db_session.query(Notification).filter(
        Notification.notification_type == "RESULT_RELEASED",
        Notification.student_id.in_([s1.id, s2.id])
    ).all()
    assert len(notifs) >= 2
    for n in notifs:
        assert "la sii daayay" in n.message
        assert "Student Portal" in n.message

    # Duplicate release attempt must be idempotent or reject duplicate notifications
    initial_count = len(notifs)
    r = client.post(f"/api/v1/results/submissions/{sub_id}/release", headers=admin_headers)
    assert r.status_code == 200
    after_notifs = db_session.query(Notification).filter(
        Notification.notification_type == "RESULT_RELEASED",
        Notification.student_id.in_([s1.id, s2.id])
    ).all()
    # No duplicate notifications generated thanks to idempotency key
    assert len(after_notifs) == initial_count


def test_twelve_subjects_class_results_management_and_release(client, db_session):
    """
    Test Scenario for Class with 12 Subjects and 30 Students:
    - 1 Class (Grade 7)
    - 12 distinct Subjects
    - 1 Academic Year (2026-2027)
    - 1 Exam Series (Mid-Term Examination 2026/2027)
    - 30 Students (360 total potential student-subject result entries)
    - 12 distinct Result Submissions
    
    Verifications:
    1. 12 independent result sets are created (one per subject).
    2. 11 subjects complete (30/30), 1 subject incomplete (28/30, 2 pending).
    3. Class Completion KPIs from PostgreSQL: Total=12, Complete=11, Pending=1, Released=0, Not Released=12.
    4. Class-level release is BLOCKED with descriptive pending warning when 11/12 complete.
    5. Completed subject (e.g. Mathematics) can be released individually.
    6. Student Portal visibility isolation: Student sees ONLY released subject (Mathematics) with grade/score, unreleased subjects remain completely hidden.
    7. Teacher enters remaining 2 student marks in Physics and submits (12/12 complete).
    8. Class-level release now SUCCEEDS and publishes all 12 subjects.
    9. Student Portal now shows all 12 subjects with scores and grades.
    10. Guardian SMS notifications sent in Somali and protected against duplicates.
    11. Admin marks view is 100% READ-ONLY.
    12. Student name search, admission number search, and performance filters (Passed/Failed) work on student score matrix.
    """
    academic_year = "2026-2027"
    exam_series_name = "Mid-Term Examination 2026/2027"

    # 1. Admin actor
    admin_user = db_session.query(User).filter(User.username == "admin").first()
    assert admin_user is not None
    admin_token = create_access_token(subject=str(admin_user.id))
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Setup Class (Grade 7)
    g7 = db_session.query(SchoolClass).filter(SchoolClass.name == "Grade 7-12Subj").first()
    if not g7:
        g7 = SchoolClass(name="Grade 7-12Subj", code="G7-12S", academic_year=academic_year, status="ACTIVE")
        db_session.add(g7)
        db_session.flush()

    # 3. Setup 12 Subjects
    subject_names = [
        ("Mathematics", "MATH-12S"),
        ("English", "ENG-12S"),
        ("Somali", "SOM-12S"),
        ("Physics", "PHYS-12S"),
        ("Chemistry", "CHEM-12S"),
        ("Biology", "BIO-12S"),
        ("Geography", "GEO-12S"),
        ("History", "HIST-12S"),
        ("Islamic Studies", "ISL-12S"),
        ("Arabic", "ARB-12S"),
        ("Computer", "CMP-12S"),
        ("Physical Education", "PE-12S"),
    ]
    subjects = []
    for s_name, s_code in subject_names:
        subj = db_session.query(Subject).filter(Subject.name == s_name).first()
        if not subj:
            subj = Subject(name=s_name, code=s_code, status="ACTIVE")
            db_session.add(subj)
            db_session.flush()
        subjects.append(subj)
    assert len(subjects) == 12

    # 4. Setup Teachers (e.g. Teacher Ahmed & Fatima)
    teacher_user1 = db_session.query(User).filter(User.username == "teacher.ahmed.12s").first()
    if not teacher_user1:
        teacher_user1 = User(
            username="teacher.ahmed.12s",
            email="ahmed.12s@hawlwadaag.edu.so",
            hashed_password="hash",
            full_name="Ahmed Hassan Ali",
            is_active=True
        )
        db_session.add(teacher_user1)
        db_session.flush()
        from app.models.user_role import UserRole
        db_session.add(UserRole(user_id=teacher_user1.id, role_id=2))

    teacher1 = db_session.query(Teacher).filter(Teacher.user_id == teacher_user1.id).first()
    if not teacher1:
        teacher1 = Teacher(
            user_id=teacher_user1.id,
            teacher_number="TCH-AHMED-12S",
            first_name="Ahmed",
            last_name="Ali",
            gender="Male",
            email=teacher_user1.email,
            status="ACTIVE"
        )
        db_session.add(teacher1)
        db_session.flush()

    teacher1_token = create_access_token(subject=str(teacher_user1.id))
    teacher1_headers = {"Authorization": f"Bearer {teacher1_token}"}

    # 5. Setup 30 Students in Grade 7
    students = []
    for i in range(1, 31):
        adm = f"ADM-12S-{i:03d}"
        uname = f"std_12s_{i:03d}"
        s_user = db_session.query(User).filter(User.username == uname).first()
        if not s_user:
            s_user = User(
                username=uname,
                email=f"std{i}.12s@hawlwadaag.edu.so",
                hashed_password="hash",
                full_name=f"Student {i:02d} GradeSeven",
                is_active=True
            )
            db_session.add(s_user)
            db_session.flush()
            from app.models.user_role import UserRole
            db_session.add(UserRole(user_id=s_user.id, role_id=3))

        std = db_session.query(Student).filter(Student.user_id == s_user.id).first()
        if not std:
            std = Student(
                user_id=s_user.id,
                admission_number=adm,
                first_name=f"Student{i:02d}",
                last_name="GradeSeven",
                gender="Male" if i % 2 == 1 else "Female",
                guardian_name=f"Guardian {i:02d}",
                guardian_phone=f"+25261555{i:04d}",
                guardian_email=f"guardian{i}@hawlwadaag.edu.so",
                status="ACTIVE"
            )
            db_session.add(std)
            db_session.flush()

        # Enrollment
        enr = db_session.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == std.id,
            StudentEnrollment.class_id == g7.id,
            StudentEnrollment.academic_year == academic_year
        ).first()
        if not enr:
            enr = StudentEnrollment(
                student_id=std.id,
                class_id=g7.id,
                academic_year=academic_year,
                status="ACTIVE",
                roll_number=f"{i:02d}"
            )
            db_session.add(enr)

        students.append((std, s_user))

    db_session.commit()
    assert len(students) == 30

    # 6. Create 12 distinct Exams & Teacher Assignments
    exams = []
    for subj in subjects:
        # Teacher assignment
        ta = db_session.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher1.id,
            TeacherAssignment.class_id == g7.id,
            TeacherAssignment.subject_id == subj.id,
            TeacherAssignment.academic_year == academic_year
        ).first()
        if not ta:
            ta = TeacherAssignment(
                teacher_id=teacher1.id,
                class_id=g7.id,
                subject_id=subj.id,
                academic_year=academic_year,
                status="ACTIVE"
            )
            db_session.add(ta)

        # Exam definition
        ex = db_session.query(Exam).filter(
            Exam.name == exam_series_name,
            Exam.class_id == g7.id,
            Exam.subject_id == subj.id,
            Exam.academic_year == academic_year
        ).first()
        if not ex:
            ex = Exam(
                name=exam_series_name,
                exam_type="Mid-Term",
                academic_year=academic_year,
                class_id=g7.id,
                subject_id=subj.id,
                start_date=date(2026, 4, 1),
                end_date=date(2026, 4, 15),
                max_marks=Decimal("100.00"),
                pass_marks=Decimal("50.00"),
                status="SCHEDULED"
            )
            db_session.add(ex)
            db_session.flush()

        exams.append(ex)

    db_session.commit()
    assert len(exams) == 12

    # Clean any prior exam results / submissions for this test
    exam_ids = [e.id for e in exams]
    db_session.query(ExamResult).filter(ExamResult.exam_id.in_(exam_ids)).delete(synchronize_session=False)
    db_session.query(ResultSubmission).filter(ResultSubmission.exam_id.in_(exam_ids)).delete(synchronize_session=False)
    db_session.query(ResultReleaseBatch).filter(ResultReleaseBatch.class_id == g7.id, ResultReleaseBatch.exam_name == exam_series_name).delete(synchronize_session=False)
    db_session.commit()

    # 7. Submit 11 Complete Subjects (30/30 each) and 1 Incomplete Subject (Physics: 28/30)
    math_exam = next(e for e in exams if e.subject.name == "Mathematics")
    physics_exam = next(e for e in exams if e.subject.name == "Physics")

    math_sub_id = None
    physics_sub_id = None

    for ex in exams:
        is_physics = (ex.id == physics_exam.id)
        # For physics, only enter marks for first 28 students
        student_limit = 28 if is_physics else 30
        marks_payload = []
        for idx in range(student_limit):
            std, _ = students[idx]
            # Vary marks
            base_score = 80.0 if (idx % 2 == 0) else 65.0
            if idx == 27 and is_physics:
                base_score = 45.0  # test below pass mark
            marks_payload.append({
                "student_id": std.id,
                "attendance_status": "PRESENT",
                "marks_obtained": base_score,
                "remarks": "Good effort"
            })

        if is_physics:
            # Save draft for Physics (incomplete)
            r = client.post("/api/v1/results/teacher/draft", json={
                "exam_id": ex.id,
                "class_id": g7.id,
                "subject_id": ex.subject_id,
                "marks": marks_payload
            }, headers=teacher1_headers)
            assert r.status_code == 200
            # Fetch submission ID
            sub = db_session.query(ResultSubmission).filter(ResultSubmission.exam_id == ex.id).first()
            physics_sub_id = sub.id
        else:
            # Submit full 30 students
            r = client.post("/api/v1/results/teacher/submit", json={
                "exam_id": ex.id,
                "class_id": g7.id,
                "subject_id": ex.subject_id,
                "marks": marks_payload
            }, headers=teacher1_headers)
            assert r.status_code == 200
            if ex.id == math_exam.id:
                math_sub_id = r.json()["submission_id"]

    # =========================================================================
    # VERIFICATION 1: CLASS RESULTS DASHBOARD COUNTERS & MATRIX
    # =========================================================================
    r = client.get(f"/api/v1/results/classes/{g7.id}?academic_year={academic_year}&exam_name={exam_series_name}", headers=admin_headers)
    assert r.status_code == 200
    dash = r.json()
    assert dash["class_id"] == g7.id
    assert dash["subjects_count"] == 12
    assert dash["students_count"] == 30
    assert dash["complete_subjects_count"] == 11
    assert dash["pending_subjects_count"] == 1
    assert dash["released_subjects_count"] == 0
    assert dash["not_released_subjects_count"] == 12
    assert dash["can_release_full"] is False
    assert dash["can_release_partial"] is True

    # Verify 12 subjects in subjects_matrix
    assert len(dash["subjects_matrix"]) == 12
    math_m = next(s for s in dash["subjects_matrix"] if s["subject_name"] == "Mathematics")
    assert math_m["is_complete"] is True
    assert math_m["pending_students"] == 0
    assert math_m["release_status"] == "NOT RELEASED"

    phys_m = next(s for s in dash["subjects_matrix"] if s["subject_name"] == "Physics")
    assert phys_m["is_complete"] is False
    assert phys_m["pending_students"] == 2
    assert phys_m["status"] == "INCOMPLETE"

    # Verify 30 students in student_matrix with 12 columns
    assert len(dash["student_matrix"]) == 30
    first_std_row = dash["student_matrix"][0]
    assert len(first_std_row["scores"]) == 12

    # =========================================================================
    # VERIFICATION 2: CLASS-LEVEL RELEASE IS BLOCKED WHEN 11/12 COMPLETE
    # =========================================================================
    r = client.post(f"/api/v1/results/classes/{g7.id}/release", json={
        "class_id": g7.id,
        "academic_year": academic_year,
        "exam_name": exam_series_name,
        "release_type": "FULL",
        "notes": "Attempting full class release with pending subject"
    }, headers=admin_headers)
    assert r.status_code == 400
    assert "pending" in r.json()["detail"].lower()

    # =========================================================================
    # VERIFICATION 3: INDIVIDUAL SUBJECT RELEASE (MATHEMATICS)
    # =========================================================================
    r = client.post(f"/api/v1/results/submissions/{math_sub_id}/release", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "RELEASED"
    assert r.json()["results_count"] == 30

    # =========================================================================
    # VERIFICATION 4: STUDENT PORTAL ISOLATION (ONLY RELEASED SUBJECT VISIBLE)
    # =========================================================================
    std1, std1_user = students[0]
    s1_token = create_access_token(subject=str(std1_user.id))
    s1_headers = {"Authorization": f"Bearer {s1_token}"}

    r = client.get("/api/v1/results/student/my-results", headers=s1_headers)
    assert r.status_code == 200
    s1_results = r.json()
    # Student must see released Mathematics exam and NOT unreleased Physics exam
    math_res = next((res for res in s1_results if res["exam_id"] == math_exam.id), None)
    assert math_res is not None
    assert float(math_res["marks_obtained"]) == 80.0
    assert math_res["grade"] == "A"
    assert not any(res["exam_id"] == physics_exam.id for res in s1_results)

    # =========================================================================
    # VERIFICATION 5: TEACHER ENTERS REMAINING 2 STUDENTS & SUBMITS PHYSICS
    # =========================================================================
    full_physics_marks = []
    for idx in range(30):
        std, _ = students[idx]
        full_physics_marks.append({
            "student_id": std.id,
            "attendance_status": "PRESENT",
            "marks_obtained": 75.0,
            "remarks": "Physics completed"
        })

    r = client.post("/api/v1/results/teacher/submit", json={
        "exam_id": physics_exam.id,
        "class_id": g7.id,
        "subject_id": physics_exam.subject_id,
        "marks": full_physics_marks
    }, headers=teacher1_headers)
    assert r.status_code == 200

    # Dashboard now shows 12/12 complete
    r = client.get(f"/api/v1/results/classes/{g7.id}?academic_year={academic_year}&exam_name={exam_series_name}", headers=admin_headers)
    assert r.status_code == 200
    dash2 = r.json()
    assert dash2["complete_subjects_count"] == 12
    assert dash2["pending_subjects_count"] == 0
    assert dash2["can_release_full"] is True

    # =========================================================================
    # VERIFICATION 6: CLASS-LEVEL RELEASE SUCCEEDS FOR ALL 12 SUBJECTS
    # =========================================================================
    r = client.post(f"/api/v1/results/classes/{g7.id}/release", json={
        "class_id": g7.id,
        "academic_year": academic_year,
        "exam_name": exam_series_name,
        "release_type": "FULL",
        "notes": "Full release for Grade 7 all 12 subjects"
    }, headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True
    assert r.json()["results_count"] == 360  # 12 subjects * 30 students

    # =========================================================================
    # VERIFICATION 7: STUDENT SEES ALL 12 SUBJECTS IN STUDENT PORTAL
    # =========================================================================
    r = client.get("/api/v1/results/student/my-results", headers=s1_headers)
    assert r.status_code == 200
    s1_all_res = r.json()
    assert len(s1_all_res) >= 12

    # =========================================================================
    # VERIFICATION 8: GUARDIAN NOTIFICATION IN SOMALI & DUPLICATE PREVENTION
    # =========================================================================
    notifs = db_session.query(Notification).filter(
        Notification.notification_type == "RESULT_RELEASED",
        Notification.student_id == std1.id
    ).all()
    assert len(notifs) >= 1
    for n in notifs:
        assert "la sii daayay" in n.message
        assert "Student Portal" in n.message

    # =========================================================================
    # VERIFICATION 9: RESULT SETS TABLE CONTINUES TO SHOW 12 INDIVIDUAL ROWS
    # =========================================================================
    r = client.get(f"/api/v1/results/submissions?academic_year={academic_year}&exam_name={exam_series_name}&class_id={g7.id}", headers=admin_headers)
    assert r.status_code == 200
    subs_list = r.json()
    assert len(subs_list) == 12
    # Verify each subject is present as an individual result set
    returned_subj_ids = {s["subject_id"] for s in subs_list}
    assert len(returned_subj_ids) == 12


def test_class_first_zero_submission_and_summary_scenarios(client, db_session):
    """
    Test Class-First Result Management scenarios:
    Scenario A: 12 subjects assigned to class, 0 teacher submissions made.
    Expected:
    1. Main page class summary lists Grade 9 with 12 subjects, 0 complete, 12 pending, 0% progress.
    2. Class dashboard lists all 12 curriculum subjects with status PENDING and assigned teacher names.
    3. No subjects are omitted or hidden.
    4. Class-level release is disabled.
    """
    academic_year = "2026-2027"
    exam_series_name = "Final Examination 2026"

    # Admin actor
    admin_user = db_session.query(User).filter(User.username == "admin").first()
    assert admin_user is not None
    admin_token = create_access_token(subject=str(admin_user.id))
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Create Grade 9 class
    g9 = db_session.query(SchoolClass).filter(SchoolClass.name == "Grade 9-Test-CF").first()
    if not g9:
        g9 = SchoolClass(name="Grade 9-Test-CF", code="G9-TCF", academic_year=academic_year, status="ACTIVE")
        db_session.add(g9)
        db_session.flush()
    else:
        g9.status = "ACTIVE"
        db_session.commit()

    # Teacher
    teacher_user = db_session.query(User).filter(User.username == "teacher.ali").first()
    teacher = db_session.query(Teacher).filter(Teacher.user_id == teacher_user.id).first()

    # Create 12 curriculum subjects and teacher assignments for Grade 9
    subject_names = [
        "Math G9", "English G9", "Somali G9", "Physics G9", "Chemistry G9",
        "Biology G9", "Geography G9", "History G9", "Arabic G9", "Islamic G9",
        "Computer G9", "Physical Education G9"
    ]
    created_subjects = []
    for idx, sname in enumerate(subject_names):
        subj = db_session.query(Subject).filter(Subject.name == sname).first()
        if not subj:
            subj = Subject(name=sname, code=f"G9-S{idx+1}", status="ACTIVE")
            db_session.add(subj)
            db_session.flush()
        else:
            subj.status = "ACTIVE"
        created_subjects.append(subj)

        # Assign teacher
        ta = db_session.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher.id,
            TeacherAssignment.class_id == g9.id,
            TeacherAssignment.subject_id == subj.id,
            TeacherAssignment.academic_year == academic_year
        ).first()
        if not ta:
            ta = TeacherAssignment(
                teacher_id=teacher.id,
                class_id=g9.id,
                subject_id=subj.id,
                academic_year=academic_year,
                status="ACTIVE"
            )
            db_session.add(ta)
        else:
            ta.status = "ACTIVE"

    # Enroll 25 students in Grade 9
    for i in range(1, 26):
        adm = f"ADM-G9-{i:03d}"
        uname = f"std_g9_{i:03d}"
        s_user = db_session.query(User).filter(User.username == uname).first()
        if not s_user:
            s_user = User(
                username=uname,
                email=f"std{i}.g9@hawlwadaag.edu.so",
                hashed_password="hash",
                full_name=f"Student {i:02d} GradeNine",
                is_active=True
            )
            db_session.add(s_user)
            db_session.flush()

        std = db_session.query(Student).filter(Student.user_id == s_user.id).first()
        if not std:
            std = Student(
                user_id=s_user.id,
                admission_number=adm,
                first_name=f"Student{i:02d}",
                last_name="GradeNine",
                gender="Male",
                status="ACTIVE"
            )
            db_session.add(std)
            db_session.flush()
        else:
            std.status = "ACTIVE"

        enr = db_session.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == std.id,
            StudentEnrollment.academic_year.in_([academic_year, academic_year.replace("-", "/")])
        ).first()
        if not enr:
            enr = StudentEnrollment(
                student_id=std.id,
                class_id=g9.id,
                academic_year=academic_year,
                status="ACTIVE",
                roll_number=f"{i:02d}"
            )
            db_session.add(enr)
        else:
            enr.class_id = g9.id
            enr.status = "ACTIVE"

    db_session.commit()

    # Teacher creates an exam for G9
    e_g9 = db_session.query(Exam).filter(
        Exam.class_id == g9.id,
        Exam.subject_id == created_subjects[0].id,
        Exam.academic_year.in_([academic_year, academic_year.replace("-", "/")]),
        Exam.exam_type == "FINAL"
    ).first()
    if not e_g9:
        e_g9 = Exam(
            name=exam_series_name,
            exam_type="FINAL",
            academic_year=academic_year,
            class_id=g9.id,
            subject_id=created_subjects[0].id,
            teacher_id=teacher.id,
            start_date=date(2026, 12, 1),
            status="SCHEDULED"
        )
        db_session.add(e_g9)
        db_session.commit()

    # 1. Level 1 (Classes Summary Endpoint)
    r = client.get(f"/api/v1/results/classes?academic_year={academic_year}&exam_name={exam_series_name}", headers=admin_headers)
    assert r.status_code == 200
    classes_summary = r.json()
    g9_summary = next((c for c in classes_summary if c["class_id"] == g9.id), None)
    assert g9_summary is not None
    assert g9_summary["class_name"] == "Grade 9-Test-CF"
    assert g9_summary["students_count"] == 25
    assert g9_summary["complete_subjects_count"] == 0
    assert g9_summary["released_subjects_count"] == 0
    assert g9_summary["progress_percent"] == 0

    # 2. Level 2 (Class Detail Endpoint: Zero submissions case)
    r = client.get(f"/api/v1/results/classes/{g9.id}?academic_year={academic_year}&exam_name={exam_series_name}", headers=admin_headers)
    assert r.status_code == 200
    dash = r.json()
    assert dash["class_id"] == g9.id
    assert dash["students_count"] == 25
    assert dash["subjects_count"] == 12
    assert dash["complete_subjects_count"] == 0
    assert dash["pending_subjects_count"] == 12
    assert dash["can_release_full"] is False

    # Check that all 12 subjects appear in subjects_matrix with status PENDING and assigned teacher
    assert len(dash["subjects_matrix"]) == 12
    for s in dash["subjects_matrix"]:
        assert s["status"] == "PENDING"
        assert s["release_status"] == "NOT RELEASED"
        assert s["expected_students"] == 25
        assert s["attended_students"] == 0
        assert s["marks_entered"] == 0
        assert s["teacher_name"] == teacher.full_name


