"""
Comprehensive Acceptance Test Suite for Somroyal EMS:
Teacher-to-Admin Exam Results Submission and Management Workflow.

Verifies all 12 Acceptance Criteria:
1. Admin creates exam -> reaches only teachers assigned to relevant subjects/classes.
2. Teachers cannot see or enter results for subjects they do not teach.
3. Teacher enters and saves marks with attendance, absence reasons, and complaints.
4. Submitting results immediately transfers sheet to Admin Results Management.
5. Submitted sheet leaves teacher active queue without deleting database records.
6. Admin CANNOT enter or edit student marks (strict 403 Forbidden backend enforcement).
7. Admin reviews telemetry: attendance, absences, absence reasons, complaints, missing marks.
8. Admin returns sheet for correction with mandatory reason; sheet unlocks for teacher.
9. Resubmitting corrected sheet preserves complete revision and audit history.
10. Approved results remain unpublished until explicit admin publication action.
11. Published results visible to individual students in Student Portal with strict isolation.
12. Other classes, subjects, teachers, and institutions remain unaffected.
"""

import pytest
from decimal import Decimal
from datetime import date, datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="module")
def setup_workflow_data(db):
    """
    Creates a dedicated, isolated test sandbox:
    - 1 Admin
    - 2 Teachers: Teacher Math (assigned Math) & Teacher Bio (assigned Biology)
    - 1 Class: 'Form 3-Alpha WF'
    - 2 Subjects: 'Workflow Mathematics' & 'Workflow Biology'
    - 3 Students: Mustaf, Amina, and Jama enrolled in Form 3-Alpha WF
    - 1 Exam series: 'Midterm Examination 2026 WF'
    """
    academic_year = "2026/2027"

    # 1. Admin User
    admin_user = db.query(User).filter(User.username == "admin").first()
    assert admin_user is not None, "Admin user must exist"
    admin_token = create_access_token(subject=str(admin_user.id))
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Ensure TEACHER and STUDENT roles exist
    r_teacher = db.query(Role).filter(Role.name == "TEACHER").first()
    if not r_teacher:
        r_teacher = Role(name="TEACHER", description="Teacher Role")
        db.add(r_teacher)
        db.flush()

    r_student = db.query(Role).filter(Role.name == "STUDENT").first()
    if not r_student:
        r_student = Role(name="STUDENT", description="Student Role")
        db.add(r_student)
        db.flush()

    # 2. Teacher A (Math)
    u_math = db.query(User).filter(User.username == "test_teacher_math_wf").first()
    if not u_math:
        u_math = User(
            username="test_teacher_math_wf",
            email="math.wf@somroyal.edu.so",
            hashed_password="hash",
            full_name="Ustad Hassan Math",
            is_active=True
        )
        db.add(u_math)
        db.flush()
        db.add(UserRole(user_id=u_math.id, role_id=r_teacher.id))
        db.flush()

    t_math = db.query(Teacher).filter(Teacher.user_id == u_math.id).first()
    if not t_math:
        t_math = Teacher(
            user_id=u_math.id,
            teacher_number="TCH-WF-MATH",
            first_name="Hassan",
            last_name="Math",
            gender="Male",
            email=u_math.email,
            status="ACTIVE"
        )
        db.add(t_math)
        db.flush()

    token_math = create_access_token(subject=str(u_math.id))
    headers_math = {"Authorization": f"Bearer {token_math}"}

    # 3. Teacher B (Biology)
    u_bio = db.query(User).filter(User.username == "test_teacher_bio_wf").first()
    if not u_bio:
        u_bio = User(
            username="test_teacher_bio_wf",
            email="bio.wf@somroyal.edu.so",
            hashed_password="hash",
            full_name="Ustad Ali Biology",
            is_active=True
        )
        db.add(u_bio)
        db.flush()
        db.add(UserRole(user_id=u_bio.id, role_id=r_teacher.id))
        db.flush()

    t_bio = db.query(Teacher).filter(Teacher.user_id == u_bio.id).first()
    if not t_bio:
        t_bio = Teacher(
            user_id=u_bio.id,
            teacher_number="TCH-WF-BIO",
            first_name="Ali",
            last_name="Biology",
            gender="Male",
            email=u_bio.email,
            status="ACTIVE"
        )
        db.add(t_bio)
        db.flush()

    token_bio = create_access_token(subject=str(u_bio.id))
    headers_bio = {"Authorization": f"Bearer {token_bio}"}

    # 4. Class: 'Form 3-Alpha WF'
    school_class = db.query(SchoolClass).filter(SchoolClass.name == "Form 3-Alpha WF").first()
    if not school_class:
        school_class = SchoolClass(
            name="Form 3-Alpha WF",
            code="F3-ALPHA-WF",
            division="SECONDARY",
            section="A",
            academic_year=academic_year,
            status="ACTIVE"
        )
        db.add(school_class)
        db.flush()

    # 5. Subjects: Math & Biology
    subj_math = db.query(Subject).filter(Subject.code == "WF-MATH-101").first()
    if not subj_math:
        subj_math = Subject(name="Workflow Mathematics", code="WF-MATH-101", status="ACTIVE")
        db.add(subj_math)
        db.flush()

    subj_bio = db.query(Subject).filter(Subject.code == "WF-BIO-101").first()
    if not subj_bio:
        subj_bio = Subject(name="Workflow Biology", code="WF-BIO-101", status="ACTIVE")
        db.add(subj_bio)
        db.flush()

    # 6. Assign Teachers:
    as_math = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == t_math.id,
        TeacherAssignment.class_id == school_class.id,
        TeacherAssignment.subject_id == subj_math.id,
        TeacherAssignment.academic_year == academic_year
    ).first()
    if not as_math:
        as_math = TeacherAssignment(
            teacher_id=t_math.id,
            class_id=school_class.id,
            subject_id=subj_math.id,
            academic_year=academic_year,
            status="ACTIVE"
        )
        db.add(as_math)

    as_bio = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == t_bio.id,
        TeacherAssignment.class_id == school_class.id,
        TeacherAssignment.subject_id == subj_bio.id,
        TeacherAssignment.academic_year == academic_year
    ).first()
    if not as_bio:
        as_bio = TeacherAssignment(
            teacher_id=t_bio.id,
            class_id=school_class.id,
            subject_id=subj_bio.id,
            academic_year=academic_year,
            status="ACTIVE"
        )
        db.add(as_bio)
    db.flush()

    # 7. Students (3 Students enrolled)
    student_records = []
    student_headers = []
    for i, s_name in enumerate(["Mustaf Farah WF", "Amina Dahir WF", "Jama Noor WF"]):
        adm_no = f"ADM-WF-00{i+1}"
        u_std = db.query(User).filter(User.username == f"std_wf_{i+1}").first()
        if not u_std:
            u_std = User(
                username=f"std_wf_{i+1}",
                email=f"std_wf_{i+1}@somroyal.edu.so",
                hashed_password="hash",
                full_name=s_name,
                is_active=True
            )
            db.add(u_std)
            db.flush()
            db.add(UserRole(user_id=u_std.id, role_id=r_student.id))
            db.flush()

        std = db.query(Student).filter(Student.admission_number == adm_no).first()
        if not std:
            std = Student(
                admission_number=adm_no,
                first_name=s_name.split()[0],
                last_name=s_name.split()[1],
                gender="Male" if i != 1 else "Female",
                user_id=u_std.id,
                status="ACTIVE"
            )
            db.add(std)
            db.flush()

        # Enroll in class
        enr = db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == std.id,
            StudentEnrollment.class_id == school_class.id,
            StudentEnrollment.academic_year == academic_year
        ).first()
        if not enr:
            enr = StudentEnrollment(
                student_id=std.id,
                class_id=school_class.id,
                academic_year=academic_year,
                roll_number=f"WF-R{i+1}",
                status="ACTIVE"
            )
            db.add(enr)
            db.flush()

        token_s = create_access_token(subject=str(u_std.id))
        student_records.append(std)
        student_headers.append({"Authorization": f"Bearer {token_s}"})

    # 8. Create official exams for both subjects
    exam_name = "Midterm Examination 2026 WF"

    math_exam = db.query(Exam).filter(
        Exam.class_id == school_class.id,
        Exam.subject_id == subj_math.id,
        Exam.academic_year == academic_year,
        Exam.name == exam_name
    ).first()
    if not math_exam:
        math_exam = Exam(
            name=exam_name,
            exam_type="MID_TERM",
            academic_year=academic_year,
            class_id=school_class.id,
            subject_id=subj_math.id,
            start_date=date(2026, 11, 1),
            max_marks=Decimal("100.00"),
            pass_marks=Decimal("50.00"),
            status="SCHEDULED"
        )
        db.add(math_exam)
        db.flush()

    bio_exam = db.query(Exam).filter(
        Exam.class_id == school_class.id,
        Exam.subject_id == subj_bio.id,
        Exam.academic_year == academic_year,
        Exam.name == exam_name
    ).first()
    if not bio_exam:
        bio_exam = Exam(
            name=exam_name,
            exam_type="MID_TERM",
            academic_year=academic_year,
            class_id=school_class.id,
            subject_id=subj_bio.id,
            start_date=date(2026, 11, 2),
            max_marks=Decimal("100.00"),
            pass_marks=Decimal("50.00"),
            status="SCHEDULED"
        )
        db.add(bio_exam)
        db.flush()

    # Clean existing submissions/results for these exams
    db.query(ExamResult).filter(ExamResult.exam_id.in_([math_exam.id, bio_exam.id])).delete(synchronize_session=False)
    db.query(ResultSubmission).filter(ResultSubmission.exam_id.in_([math_exam.id, bio_exam.id])).delete(synchronize_session=False)
    db.commit()

    return {
        "academic_year": academic_year,
        "exam_name": exam_name,
        "admin_headers": admin_headers,
        "headers_math": headers_math,
        "headers_bio": headers_bio,
        "t_math": t_math,
        "t_bio": t_bio,
        "school_class": school_class,
        "subj_math": subj_math,
        "subj_bio": subj_bio,
        "math_exam": math_exam,
        "bio_exam": bio_exam,
        "students": student_records,
        "student_headers": student_headers,
    }


# =============================================================================
# ACCEPTANCE TEST 1 & 2: EXAM REACHES ONLY ASSIGNED TEACHER (NO LEAKAGE)
# =============================================================================
def test_acceptance_1_and_2_teacher_assignment_isolation(client, setup_workflow_data):
    """
    Criterion 1: Admin created exam reaches ONLY teachers assigned to relevant subjects/classes.
    Criterion 2: Teachers CANNOT see or enter results for subjects they do not teach.
    """
    data = setup_workflow_data
    headers_math = data["headers_math"]
    headers_bio = data["headers_bio"]
    math_exam = data["math_exam"]
    bio_exam = data["bio_exam"]

    # Teacher Math views assigned exams via results workflow API
    res_m = client.get("/api/v1/results/teacher/assignments", headers=headers_math)
    assert res_m.status_code == 200
    math_tasks = res_m.json()
    math_exam_ids = [t["exam_id"] for t in math_tasks]

    # Must contain Math exam, must NOT contain Bio exam
    assert math_exam.id in math_exam_ids, "Teacher Math must receive Math exam task"
    assert bio_exam.id not in math_exam_ids, "Teacher Math must NOT receive Biology exam task"

    # Teacher Bio views assigned exams
    res_b = client.get("/api/v1/results/teacher/assignments", headers=headers_bio)
    assert res_b.status_code == 200
    bio_tasks = res_b.json()
    bio_exam_ids = [t["exam_id"] for t in bio_tasks]

    # Must contain Bio exam, must NOT contain Math exam
    assert bio_exam.id in bio_exam_ids, "Teacher Bio must receive Biology exam task"
    assert math_exam.id not in bio_exam_ids, "Teacher Bio must NOT receive Math exam task"

    # Teacher Math tries to fetch roster for Biology -> 403 Forbidden
    res_idor_roster = client.get(f"/api/v1/results/teacher/exams/{bio_exam.id}/roster", headers=headers_math)
    assert res_idor_roster.status_code == 403, "Teacher Math accessing Bio exam roster must be rejected with 403"

    # Teacher Math tries to save marks on Biology exam -> 403 Forbidden
    idor_draft_payload = {
        "exam_id": bio_exam.id,
        "class_id": data["school_class"].id,
        "subject_id": data["subj_bio"].id,
        "marks": []
    }
    res_idor_draft = client.post("/api/v1/results/teacher/draft", json=idor_draft_payload, headers=headers_math)
    assert res_idor_draft.status_code == 403, "Teacher Math saving marks on Bio exam must be rejected with 403"


# =============================================================================
# ACCEPTANCE TEST 3: TEACHER ENTERS AND SAVES MARKS, ABSENCES & COMPLAINTS
# =============================================================================
def test_acceptance_3_teacher_enters_marks_absences_and_complaints(client, setup_workflow_data, db):
    """
    Criterion 3:
    - Teacher enters valid marks (0 <= marks <= max_marks).
    - Preserves absence without forcing zero marks.
    - Saves absence reasons and exam complaints.
    - Rejects invalid marks (> max_marks or < 0).
    """
    data = setup_workflow_data
    headers_math = data["headers_math"]
    math_exam = data["math_exam"]
    school_class = data["school_class"]
    subj_math = data["subj_math"]
    students = data["students"]

    # 1. Validation test: marks > 100 or marks < 0
    invalid_high_payload = {
        "exam_id": math_exam.id,
        "class_id": school_class.id,
        "subject_id": subj_math.id,
        "marks": [
            {
                "student_id": students[0].id,
                "attendance_status": "PRESENT",
                "marks_obtained": 105.00,  # Max is 100
            }
        ]
    }
    res_high = client.post("/api/v1/results/teacher/draft", json=invalid_high_payload, headers=headers_math)
    assert res_high.status_code in (400, 422), "Marks > max_marks must be rejected"

    invalid_neg_payload = {
        "exam_id": math_exam.id,
        "class_id": school_class.id,
        "subject_id": subj_math.id,
        "marks": [
            {
                "student_id": students[0].id,
                "attendance_status": "PRESENT",
                "marks_obtained": -5.00,
            }
        ]
    }
    res_neg = client.post("/api/v1/results/teacher/draft", json=invalid_neg_payload, headers=headers_math)
    assert res_neg.status_code in (400, 422), "Negative marks must be rejected"

    # 2. Enter valid marks with attendance, absence reasons, and complaints
    valid_draft_payload = {
        "exam_id": math_exam.id,
        "class_id": school_class.id,
        "subject_id": subj_math.id,
        "marks": [
            {
                "student_id": students[0].id,
                "attendance_status": "PRESENT",
                "marks_obtained": 86.50,
                "remarks": "Solid problem-solving skills."
            },
            {
                "student_id": students[1].id,
                "attendance_status": "ABSENT",
                "absence_reason": "Severe malaria, admitted at Banadir Hospital",
                "marks_obtained": None,
                "remarks": "Excused sick leave"
            },
            {
                "student_id": students[2].id,
                "attendance_status": "PRESENT",
                "marks_obtained": 94.00,
                "complaint": "Question 4 on Euclidean geometry had blurry printing",
                "remarks": "Outstanding test score"
            }
        ]
    }
    res_draft = client.post("/api/v1/results/teacher/draft", json=valid_draft_payload, headers=headers_math)
    assert res_draft.status_code == 200, res_draft.text
    assert res_draft.json()["success"] is True

    # 3. Verify in database: Absent student marks_obtained MUST be None (not 0.00!)
    r_abs = db.query(ExamResult).filter(ExamResult.exam_id == math_exam.id, ExamResult.student_id == students[1].id).first()
    assert r_abs is not None
    assert r_abs.attendance_status == "ABSENT"
    assert r_abs.marks_obtained is None, "Absent student must NOT be forced to 0!"
    assert r_abs.absence_reason == "Severe malaria, admitted at Banadir Hospital"

    # Verify complaint
    r_comp = db.query(ExamResult).filter(ExamResult.exam_id == math_exam.id, ExamResult.student_id == students[2].id).first()
    assert r_comp is not None
    assert r_comp.complaint == "Question 4 on Euclidean geometry had blurry printing"


# =============================================================================
# ACCEPTANCE TEST 4 & 5: SUBMIT RESULTS TO ADMIN & LOCK TEACHER EDITING
# =============================================================================
def test_acceptance_4_and_5_submit_transfers_and_locks(client, setup_workflow_data, db):
    """
    Criterion 4: Submitting results sheet immediately makes it available in Admin Results Management.
    Criterion 5: The submitted sheet leaves the teacher's active editable queue without deleting DB records.
    """
    data = setup_workflow_data
    headers_math = data["headers_math"]
    admin_headers = data["admin_headers"]
    math_exam = data["math_exam"]
    school_class = data["school_class"]
    subj_math = data["subj_math"]
    students = data["students"]

    submit_payload = {
        "exam_id": math_exam.id,
        "class_id": school_class.id,
        "subject_id": subj_math.id,
        "marks": [
            {
                "student_id": students[0].id,
                "attendance_status": "PRESENT",
                "marks_obtained": 86.50,
                "remarks": "Solid problem-solving skills."
            },
            {
                "student_id": students[1].id,
                "attendance_status": "ABSENT",
                "absence_reason": "Severe malaria, admitted at Banadir Hospital",
                "marks_obtained": None,
                "remarks": "Excused sick leave"
            },
            {
                "student_id": students[2].id,
                "attendance_status": "PRESENT",
                "marks_obtained": 94.00,
                "complaint": "Question 4 on Euclidean geometry had blurry printing",
                "remarks": "Outstanding test score"
            }
        ]
    }

    # Teacher submits
    res_submit = client.post("/api/v1/results/teacher/submit", json=submit_payload, headers=headers_math)
    assert res_submit.status_code == 200, res_submit.text
    sub_resp = res_submit.json()
    assert sub_resp["status"] == "SUBMITTED"
    submission_id = sub_resp["submission_id"]

    # 1. Immediately available in Admin Results Management
    res_admin_list = client.get("/api/v1/results/submissions?exam_type=MID_TERM", headers=admin_headers)
    assert res_admin_list.status_code == 200
    all_subs = res_admin_list.json()
    admin_sub = next((s for s in all_subs if s["id"] == submission_id), None)
    assert admin_sub is not None, "Submitted sheet must appear in Admin submissions list"
    assert admin_sub["status"] == "SUBMITTED"
    assert "Hassan Math" in admin_sub["teacher_name"]
    assert admin_sub["subject_name"] == "Workflow Mathematics"

    # 2. Teacher active queue lock: cannot silently modify or recall
    res_edit_attempt = client.post("/api/v1/results/teacher/draft", json=submit_payload, headers=headers_math)
    assert res_edit_attempt.status_code == 400, "Teacher must NOT be allowed to edit a SUBMITTED sheet"

    res_resubmit_attempt = client.post("/api/v1/results/teacher/submit", json=submit_payload, headers=headers_math)
    assert res_resubmit_attempt.status_code in (400, 409), "Duplicate submission while SUBMITTED must be blocked"

    # 3. Database records remain intact
    count = db.query(ExamResult).filter(ExamResult.exam_id == math_exam.id).count()
    assert count == 3, "Database records must NOT be deleted upon queue transition"


# =============================================================================
# ACCEPTANCE TEST 6: ADMIN CANNOT ENTER OR EDIT MARKS (BACKEND 403 ENFORCEMENT)
# =============================================================================
def test_acceptance_6_admin_cannot_enter_or_edit_marks(client, setup_workflow_data):
    """
    Criterion 6:
    The administrator must NOT have a form for manually entering or filling students' marks.
    Enforced in the backend API: POST /api/v1/exams/{id}/results blocks Admin with 403 Forbidden.
    """
    data = setup_workflow_data
    admin_headers = data["admin_headers"]
    math_exam = data["math_exam"]
    students = data["students"]

    admin_mark_entry_payload = {
        "exam_id": math_exam.id,
        "results": [
            {
                "student_id": students[0].id,
                "attendance_status": "PRESENT",
                "marks_obtained": 99.00
            }
        ]
    }

    res = client.post(f"/api/v1/exams/{math_exam.id}/results", json=admin_mark_entry_payload, headers=admin_headers)
    assert res.status_code == 403, f"Admin must receive 403 Forbidden when attempting to record marks, got {res.status_code}"
    detail = res.json().get("detail", "")
    assert "Administrators cannot enter or modify examination marks" in detail or "Only teachers can record exam results" in detail


# =============================================================================
# ACCEPTANCE TEST 7: ADMIN REVIEWS ATTENDANCE, REASONS, COMPLAINTS & TELEMETRY
# =============================================================================
def test_acceptance_7_admin_reviews_attendance_and_telemetry(client, setup_workflow_data, db):
    """
    Criterion 7:
    Admin reviews roster telemetry: expected, sat exam, absent, recorded reasons, complaints, missing marks.
    """
    data = setup_workflow_data
    admin_headers = data["admin_headers"]
    math_exam = data["math_exam"]

    sub = db.query(ResultSubmission).filter(ResultSubmission.exam_id == math_exam.id).first()
    assert sub is not None, "Submission must exist in database"

    res_rev = client.get(f"/api/v1/results/submissions/{sub.id}", headers=admin_headers)
    assert res_rev.status_code == 200
    rev_data = res_rev.json()

    # Exact calculated counts
    assert rev_data["expected_students"] == 3
    assert rev_data["sat_exam_students"] == 2
    assert rev_data["absent_students"] == 1
    assert rev_data["missing_marks_students"] == 0
    assert rev_data["recorded_absence_reasons_count"] == 1
    assert rev_data["complaints_count"] == 1

    # Student list details
    students_list = rev_data["students"]
    abs_st = next(s for s in students_list if s["attendance_status"] == "ABSENT")
    assert abs_st["absence_reason"] == "Severe malaria, admitted at Banadir Hospital"

    comp_st = next(s for s in students_list if s["complaint"])
    assert "blurry printing" in comp_st["complaint"]


# =============================================================================
# ACCEPTANCE TEST 8 & 9: RETURN FOR CORRECTION, RESUBMIT & REVISION AUDIT TRAIL
# =============================================================================
def test_acceptance_8_and_9_return_correction_and_revisions(client, setup_workflow_data, db):
    """
    Criterion 8: Admin returns sheet with required explanation; task reappears in teacher queue.
    Criterion 9: Teacher resubmits; revision history and audit trail are preserved.
    """
    data = setup_workflow_data
    admin_headers = data["admin_headers"]
    headers_math = data["headers_math"]
    math_exam = data["math_exam"]
    school_class = data["school_class"]
    subj_math = data["subj_math"]
    students = data["students"]

    sub = db.query(ResultSubmission).filter(ResultSubmission.exam_id == math_exam.id).first()
    assert sub is not None

    # 1. Mandatory explanation check
    res_empty_reason = client.post(f"/api/v1/results/submissions/{sub.id}/return", json={"reason": ""}, headers=admin_headers)
    assert res_empty_reason.status_code in (400, 422), "Admin return without reason must be rejected"

    # 2. Return with valid explanation
    return_reason = "Please re-verify Student 1 score; Banadir medical cert accepted for Student 2."
    res_return = client.post(f"/api/v1/results/submissions/{sub.id}/return", json={"reason": return_reason}, headers=admin_headers)
    assert res_return.status_code == 200
    assert res_return.json()["status"] == "RETURNED"

    # 3. Task reappears as editable in Teacher Math's active queue
    res_roster = client.get(f"/api/v1/results/teacher/exams/{math_exam.id}/roster", headers=headers_math)
    assert res_roster.status_code == 200
    roster_data = res_roster.json()
    assert roster_data["is_locked"] is False, "Returned sheet must be unlocked for teacher editing"
    assert roster_data["submission_status"] == "RETURNED"
    assert roster_data["return_reason"] == return_reason

    # 4. Teacher corrects Student 1 marks: from 86.50 to 91.00
    corrected_payload = {
        "exam_id": math_exam.id,
        "class_id": school_class.id,
        "subject_id": subj_math.id,
        "marks": [
            {
                "student_id": students[0].id,
                "attendance_status": "PRESENT",
                "marks_obtained": 91.00,
                "remarks": "Re-verified paper mark."
            },
            {
                "student_id": students[1].id,
                "attendance_status": "ABSENT",
                "absence_reason": "Severe malaria, admitted at Banadir Hospital",
                "marks_obtained": None,
                "remarks": "Medical certificate verified"
            },
            {
                "student_id": students[2].id,
                "attendance_status": "PRESENT",
                "marks_obtained": 94.00,
                "complaint": "Question 4 on Euclidean geometry had blurry printing",
                "remarks": "Outstanding test score"
            }
        ]
    }
    res_resubmit = client.post("/api/v1/results/teacher/submit", json=corrected_payload, headers=headers_math)
    assert res_resubmit.status_code == 200
    assert res_resubmit.json()["status"] == "SUBMITTED"

    # 5. Verify revision history preserved
    res_rev_detail = client.get(f"/api/v1/results/submissions/{sub.id}", headers=admin_headers)
    revisions = res_rev_detail.json().get("revisions", [])
    assert len(revisions) >= 3, f"Must have at least 3 revision events, got {len(revisions)}"
    actions = [r["action"] for r in revisions]
    assert "SUBMITTED" in actions
    assert any("RETURN" in a for a in actions), f"Return event must be recorded, got: {actions}"
    assert "RESUBMITTED" in actions


# =============================================================================
# ACCEPTANCE TEST 10 & 11: APPROVAL SEPARATE FROM PUBLISH & STUDENT VISIBILITY
# =============================================================================
def test_acceptance_10_and_11_approve_and_publish_separation(client, setup_workflow_data, db):
    """
    Criterion 10: Approved results remain unpublished until explicit publication.
    Criterion 11: Students see only their own published results.
    """
    data = setup_workflow_data
    admin_headers = data["admin_headers"]
    math_exam = data["math_exam"]
    students = data["students"]
    student_headers = data["student_headers"]

    sub = db.query(ResultSubmission).filter(ResultSubmission.exam_id == math_exam.id).first()
    assert sub is not None

    # 1. Admin Approves result sheet
    res_app = client.post(f"/api/v1/results/submissions/{sub.id}/approve", json={}, headers=admin_headers)
    assert res_app.status_code == 200
    assert res_app.json()["status"] == "APPROVED"

    # 2. Results must NOT be visible to student yet!
    res_s1_before = client.get("/api/v1/results/student/my-results", headers=student_headers[0])
    assert res_s1_before.status_code == 200
    exams_s1_before = res_s1_before.json()
    assert not any(e["exam_id"] == math_exam.id for e in exams_s1_before), "Approved result must NOT be visible before release"

    # 3. Admin Publishes the result sheet
    res_pub = client.post(f"/api/v1/results/submissions/{sub.id}/release", headers=admin_headers)
    assert res_pub.status_code == 200
    assert res_pub.json()["status"] == "RELEASED"

    # 4. Now Student 1 sees their published result
    res_s1_after = client.get("/api/v1/results/student/my-results", headers=student_headers[0])
    assert res_s1_after.status_code == 200
    exams_s1_after = res_s1_after.json()
    s1_math = next((e for e in exams_s1_after if e["exam_id"] == math_exam.id), None)
    assert s1_math is not None, "Released result must now be visible to Student 1"
    assert float(s1_math["marks_obtained"]) == 91.0
    assert s1_math["status"] == "RELEASED"

    # 5. Isolation: Student 2 sees their own result (absent), NOT student 1's marks
    res_s2_after = client.get("/api/v1/results/student/my-results", headers=student_headers[1])
    assert res_s2_after.status_code == 200
    exams_s2_after = res_s2_after.json()
    s2_math = next((e for e in exams_s2_after if e["exam_id"] == math_exam.id), None)
    assert s2_math is not None
    assert s2_math["attendance_status"] == "ABSENT"
    assert s2_math["marks_obtained"] is None


# =============================================================================
# ACCEPTANCE TEST 12: OTHER CLASSES, SUBJECTS & TEACHERS REMAIN UNAFFECTED
# =============================================================================
def test_acceptance_12_non_interference_and_isolation(client, setup_workflow_data, db):
    """
    Criterion 12:
    Other classes, subjects, teachers, and existing records remain completely unaffected.
    """
    data = setup_workflow_data
    headers_bio = data["headers_bio"]
    bio_exam = data["bio_exam"]

    # Teacher Bio's task remains in active queue, unaffected by Math submission & approval
    res_b = client.get("/api/v1/results/teacher/assignments", headers=headers_bio)
    assert res_b.status_code == 200
    bio_tasks = res_b.json()
    b_task = next(t for t in bio_tasks if t["exam_id"] == bio_exam.id)
    # Verify Teacher Bio's roster is accessible and not locked
    res_b_roster = client.get(f"/api/v1/results/teacher/exams/{bio_exam.id}/roster", headers=headers_bio)
    assert res_b_roster.status_code == 200
    assert res_b_roster.json()["is_locked"] is False
