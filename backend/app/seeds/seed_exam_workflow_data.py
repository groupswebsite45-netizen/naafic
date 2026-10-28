import os
import sys
from decimal import Decimal
from datetime import date, datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.core.database import SessionLocal
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.exam import Exam, ExamResult
from app.models.result_submission import ResultSubmission
from app.models.user import User
from app.models.user_role import UserRole
from app.core.grading import calculate_grade


def seed_exam_workflow():
    db = SessionLocal()
    try:
        academic_year = "2025-2026"
        exam_name = "Final Examination 2026"

        # 1. Ensure Admin User
        admin_user = db.query(User).filter(User.username == "admin").first()

        from sqlalchemy import or_

        # Ahmed Hassan (Math, Science)
        ahmed_user = db.query(User).filter(
            or_(User.username == "ahmed_hassan", User.email == "ahmed.hassan@hawlwadaagschool.edu.so")
        ).first()
        if not ahmed_user:
            ahmed_user = User(
                username="ahmed_hassan",
                email="ahmed.hassan@hawlwadaagschool.edu.so",
                hashed_password="hashed_pass_ahmed",
                full_name="Ahmed Hassan Warsame",
                is_active=True
            )
            db.add(ahmed_user)
            db.flush()
            db.add(UserRole(user_id=ahmed_user.id, role_id=2))
            db.flush()

        ahmed_tch = db.query(Teacher).filter(
            or_(Teacher.user_id == ahmed_user.id, Teacher.email == ahmed_user.email)
        ).first()
        if not ahmed_tch:
            ahmed_tch = Teacher(
                user_id=ahmed_user.id,
                teacher_number="TCH-2026-001",
                first_name="Ahmed",
                middle_name="Hassan",
                last_name="Warsame",
                gender="Male",
                email=ahmed_user.email,
                qualification="B.Sc. Mathematics & Physics",
                status="ACTIVE"
            )
            db.add(ahmed_tch)
            db.flush()

        # Fadumo Warsame (English)
        fadumo_user = db.query(User).filter(
            or_(User.username == "fadumo_warsame", User.email == "fadumo.warsame@hawlwadaagschool.edu.so")
        ).first()
        if not fadumo_user:
            fadumo_user = User(
                username="fadumo_warsame",
                email="fadumo.warsame@hawlwadaagschool.edu.so",
                hashed_password="hashed_pass_fadumo",
                full_name="Fatima Warsame Ali",
                is_active=True
            )
            db.add(fadumo_user)
            db.flush()
            db.add(UserRole(user_id=fadumo_user.id, role_id=2))
            db.flush()

        fadumo_tch = db.query(Teacher).filter(
            or_(Teacher.user_id == fadumo_user.id, Teacher.email == fadumo_user.email)
        ).first()
        if not fadumo_tch:
            fadumo_tch = Teacher(
                user_id=fadumo_user.id,
                teacher_number="TCH-2026-002",
                first_name="Fatima",
                last_name="Warsame",
                gender="Female",
                email=fadumo_user.email,
                qualification="B.Ed. English Literature",
                status="ACTIVE"
            )
            db.add(fadumo_tch)
            db.flush()

        # Sheikh Abdirahman (Islamic & Arabic)
        sheikh_user = db.query(User).filter(
            or_(User.username == "sheikh_abdirahman", User.email == "sheikh.abdirahman@hawlwadaagschool.edu.so")
        ).first()
        if not sheikh_user:
            sheikh_user = User(
                username="sheikh_abdirahman",
                email="sheikh.abdirahman@hawlwadaagschool.edu.so",
                hashed_password="hashed_pass_sheikh",
                full_name="Sheikh Abdirahman Yusuf",
                is_active=True
            )
            db.add(sheikh_user)
            db.flush()
            db.add(UserRole(user_id=sheikh_user.id, role_id=2))
            db.flush()

        sheikh_tch = db.query(Teacher).filter(
            or_(Teacher.user_id == sheikh_user.id, Teacher.email == sheikh_user.email)
        ).first()
        if not sheikh_tch:
            sheikh_tch = Teacher(
                user_id=sheikh_user.id,
                teacher_number="TCH-2026-003",
                first_name="Sheikh",
                last_name="Abdirahman",
                gender="Male",
                email=sheikh_user.email,
                qualification="M.A. Islamic Studies & Arabic",
                status="ACTIVE"
            )
            db.add(sheikh_tch)
            db.flush()

        # 3. Ensure Classes
        g7 = db.query(SchoolClass).filter(SchoolClass.name == "Grade 7").first()
        g8 = db.query(SchoolClass).filter(SchoolClass.name == "Grade 8").first()

        # 4. Subjects
        math = db.query(Subject).filter(Subject.name == "Mathematics").first()
        eng = db.query(Subject).filter(Subject.name.ilike("%English%")).first()
        sci = db.query(Subject).filter(Subject.name.ilike("%Science%")).first()
        isl = db.query(Subject).filter(Subject.name.ilike("%Islamic%")).first()

        subjects = [s for s in (math, eng, sci, isl) if s]

        # 5. Teacher Assignments
        # Ahmed -> G7 Math, G7 Science, G8 Math
        assignments_spec = [
            (ahmed_tch, g7, math),
            (ahmed_tch, g7, sci),
            (ahmed_tch, g8, math),
            (fadumo_tch, g7, eng),
            (sheikh_tch, g7, isl),
        ]

        for tch, cls_obj, subj_obj in assignments_spec:
            if not cls_obj or not subj_obj:
                continue
            ta = db.query(TeacherAssignment).filter(
                TeacherAssignment.teacher_id == tch.id,
                TeacherAssignment.class_id == cls_obj.id,
                TeacherAssignment.subject_id == subj_obj.id,
                TeacherAssignment.academic_year == academic_year
            ).first()
            if not ta:
                ta = TeacherAssignment(
                    teacher_id=tch.id,
                    class_id=cls_obj.id,
                    subject_id=subj_obj.id,
                    academic_year=academic_year,
                    status="ACTIVE"
                )
                db.add(ta)

        db.flush()

        # 6. Ensure Exams exist for Grade 7 & 8
        created_exams = {}
        for cls_obj in (g7, g8):
            if not cls_obj:
                continue
            for subj_obj in subjects:
                ex = db.query(Exam).filter(
                    Exam.class_id == cls_obj.id,
                    Exam.subject_id == subj_obj.id,
                    Exam.academic_year == academic_year,
                    Exam.name == exam_name
                ).first()
                if not ex:
                    ex = Exam(
                        name=exam_name,
                        exam_type="Final",
                        academic_year=academic_year,
                        class_id=cls_obj.id,
                        subject_id=subj_obj.id,
                        start_date=date(2026, 10, 20),
                        max_marks=Decimal("100.00"),
                        pass_marks=Decimal("50.00"),
                        status="SCHEDULED"
                    )
                    db.add(ex)
                    db.flush()
                created_exams[(cls_obj.id, subj_obj.id)] = ex

        # 7. Get enrolled students in Grade 7
        g7_enrollments = db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == g7.id,
            StudentEnrollment.academic_year == academic_year,
            StudentEnrollment.status == "ACTIVE"
        ).all()

        enrolled_g7_count = len(g7_enrollments)

        # 8. Seed Submissions in Realistic States:
        # A) English Grade 7: APPROVED (Submitted by Fadumo, Approved by Admin)
        if (g7.id, eng.id) in created_exams:
            ex_eng = created_exams[(g7.id, eng.id)]
            sub_eng = db.query(ResultSubmission).filter(ResultSubmission.exam_id == ex_eng.id).first()
            if not sub_eng:
                sub_eng = ResultSubmission(
                    exam_id=ex_eng.id,
                    class_id=g7.id,
                    subject_id=eng.id,
                    teacher_id=fadumo_tch.id,
                    academic_year=academic_year,
                    exam_name=exam_name,
                    status="APPROVED",
                    expected_students=enrolled_g7_count,
                    completed_students=enrolled_g7_count,
                    pending_students=0,
                    submitted_at=datetime(2026, 10, 16, 10, 0, tzinfo=timezone.utc),
                    submitted_by_id=fadumo_user.id,
                    approved_at=datetime(2026, 10, 17, 14, 0, tzinfo=timezone.utc),
                    approved_by_id=admin_user.id if admin_user else None
                )
                db.add(sub_eng)
                db.flush()

                # Results for all students in English
                for idx, enr in enumerate(g7_enrollments):
                    m = Decimal("78.00") if idx % 2 == 0 else Decimal("85.50")
                    grd, rem, _ = calculate_grade(m, ex_eng.max_marks)
                    r = ExamResult(
                        exam_id=ex_eng.id,
                        class_id=g7.id,
                        student_id=enr.student_id,
                        subject_id=eng.id,
                        submission_id=sub_eng.id,
                        attendance_status="PRESENT",
                        marks_obtained=m,
                        grade=grd,
                        remarks="Approved score",
                        status="APPROVED",
                        recorded_by_id=fadumo_user.id
                    )
                    db.add(r)

        # B) Mathematics Grade 7: SUBMITTED (Submitted by Ahmed, awaiting Admin review)
        if (g7.id, math.id) in created_exams:
            ex_math = created_exams[(g7.id, math.id)]
            sub_math = db.query(ResultSubmission).filter(ResultSubmission.exam_id == ex_math.id).first()
            if not sub_math:
                sub_math = ResultSubmission(
                    exam_id=ex_math.id,
                    class_id=g7.id,
                    subject_id=math.id,
                    teacher_id=ahmed_tch.id,
                    academic_year=academic_year,
                    exam_name=exam_name,
                    status="SUBMITTED",
                    expected_students=enrolled_g7_count,
                    completed_students=enrolled_g7_count,
                    pending_students=0,
                    submitted_at=datetime(2026, 10, 16, 11, 30, tzinfo=timezone.utc),
                    submitted_by_id=ahmed_user.id
                )
                db.add(sub_math)
                db.flush()

                for idx, enr in enumerate(g7_enrollments):
                    att = "ABSENT" if idx == 1 else "PRESENT"
                    m = None if att == "ABSENT" else (Decimal("92.00") if idx == 0 else Decimal("68.00"))
                    grd = None if att == "ABSENT" else calculate_grade(m, ex_math.max_marks)[0]
                    r = ExamResult(
                        exam_id=ex_math.id,
                        class_id=g7.id,
                        student_id=enr.student_id,
                        subject_id=math.id,
                        submission_id=sub_math.id,
                        attendance_status=att,
                        marks_obtained=m,
                        grade=grd,
                        remarks=att if att == "ABSENT" else "Submitted score",
                        status="SUBMITTED",
                        recorded_by_id=ahmed_user.id
                    )
                    db.add(r)

        # C) Science Grade 7: PARTIAL (Ahmed Hassan entered only some marks)
        if (g7.id, sci.id) in created_exams:
            ex_sci = created_exams[(g7.id, sci.id)]
            sub_sci = db.query(ResultSubmission).filter(ResultSubmission.exam_id == ex_sci.id).first()
            if not sub_sci and enrolled_g7_count > 1:
                half_count = max(1, enrolled_g7_count // 2)
                sub_sci = ResultSubmission(
                    exam_id=ex_sci.id,
                    class_id=g7.id,
                    subject_id=sci.id,
                    teacher_id=ahmed_tch.id,
                    academic_year=academic_year,
                    exam_name=exam_name,
                    status="PARTIAL",
                    expected_students=enrolled_g7_count,
                    completed_students=half_count,
                    pending_students=enrolled_g7_count - half_count
                )
                db.add(sub_sci)
                db.flush()

                for idx in range(half_count):
                    enr = g7_enrollments[idx]
                    m = Decimal("74.00")
                    grd, rem, _ = calculate_grade(m, ex_sci.max_marks)
                    r = ExamResult(
                        exam_id=ex_sci.id,
                        class_id=g7.id,
                        student_id=enr.student_id,
                        subject_id=sci.id,
                        submission_id=sub_sci.id,
                        attendance_status="PRESENT",
                        marks_obtained=m,
                        grade=grd,
                        remarks="Draft mark",
                        status="DRAFT",
                        recorded_by_id=ahmed_user.id
                    )
                    db.add(r)

        db.commit()
        print("Successfully seeded Hawlwadaag School realistic exam result workflow data in PostgreSQL!")

    except Exception as e:
        db.rollback()
        print("Error seeding data:", e)
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_exam_workflow()
