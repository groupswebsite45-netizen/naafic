import pytest
from fastapi import HTTPException
from app.core.database import SessionLocal
from app.models.teacher import Teacher
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.teacher_assignment import TeacherAssignment
from app.services.teacher_service import TeacherService
from app.services.class_service import ClassService
from app.services.subject_service import SubjectService
from app.schemas.teacher import (
    TeacherAssignmentCreate,
    TeacherAssignmentUpdate,
    TeacherBulkAssignmentItem
)


@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()


def test_duplicate_teacher_assignment_scenarios(db_session):
    teacher_service = TeacherService(db_session)

    # 1. Setup or retrieve test teachers, classes, subjects
    t_a = db_session.query(Teacher).filter(Teacher.status == "ACTIVE").first()
    t_b = db_session.query(Teacher).filter(Teacher.status == "ACTIVE", Teacher.id != t_a.id).first()
    classes = db_session.query(SchoolClass).filter(SchoolClass.status == "ACTIVE").limit(2).all()
    c_1, c_2 = classes[0], classes[1]
    subjects = db_session.query(Subject).filter(Subject.status == "ACTIVE").limit(2).all()
    s_arabic, s_math = subjects[0], subjects[1]

    academic_year = "2028-2029"  # distinct test academic year

    # Cleanup any prior test assignments in this academic year
    db_session.query(TeacherAssignment).filter(
        TeacherAssignment.academic_year.in_([academic_year, academic_year.replace('-', '/')]),
        TeacherAssignment.class_id.in_([c_1.id, c_2.id])
    ).delete(synchronize_session=False)
    db_session.commit()

    try:
        # Scenario 1: Class 1 + Arabic + Teacher A = Allowed
        assign_1 = teacher_service.assign_class_subject(
            teacher_id=t_a.id,
            data=TeacherAssignmentCreate(
                class_id=c_1.id,
                subject_id=s_arabic.id,
                academic_year=academic_year
            )
        )
        assert assign_1 is not None
        assert assign_1.teacher_id == t_a.id
        assert assign_1.class_id == c_1.id
        assert assign_1.subject_id == s_arabic.id

        # Scenario 2: Class 1 + Arabic + Teacher B = BLOCKED
        with pytest.raises(HTTPException) as exc_info:
            teacher_service.assign_class_subject(
                teacher_id=t_b.id,
                data=TeacherAssignmentCreate(
                    class_id=c_1.id,
                    subject_id=s_arabic.id,
                    academic_year=academic_year
                )
            )
        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "This subject is already assigned to another teacher in this class."

        # Scenario 3: Class 1 + Mathematics + Teacher B = Allowed
        assign_3 = teacher_service.assign_class_subject(
            teacher_id=t_b.id,
            data=TeacherAssignmentCreate(
                class_id=c_1.id,
                subject_id=s_math.id,
                academic_year=academic_year
            )
        )
        assert assign_3 is not None
        assert assign_3.teacher_id == t_b.id
        assert assign_3.class_id == c_1.id
        assert assign_3.subject_id == s_math.id

        # Scenario 4: Class 2 + Arabic + Teacher B = Allowed
        assign_4 = teacher_service.assign_class_subject(
            teacher_id=t_b.id,
            data=TeacherAssignmentCreate(
                class_id=c_2.id,
                subject_id=s_arabic.id,
                academic_year=academic_year
            )
        )
        assert assign_4 is not None
        assert assign_4.teacher_id == t_b.id
        assert assign_4.class_id == c_2.id
        assert assign_4.subject_id == s_arabic.id

        # Scenario 5: Check availability endpoint logic
        check_blocked = teacher_service.check_assignment_availability(
            class_id=c_1.id,
            subject_id=s_arabic.id,
            academic_year=academic_year,
            teacher_id=t_b.id
        )
        assert check_blocked["available"] is False
        assert check_blocked["message"] == "This subject is already assigned to another teacher in this class."

        check_allowed_same = teacher_service.check_assignment_availability(
            class_id=c_1.id,
            subject_id=s_arabic.id,
            academic_year=academic_year,
            teacher_id=t_a.id
        )
        assert check_allowed_same["available"] is True
        assert check_allowed_same["is_same_teacher"] is True

        # Scenario 6: Re-assigning duplicate on POST raises conflict for same teacher
        with pytest.raises(HTTPException) as exc_same_dup:
            teacher_service.assign_class_subject(
                teacher_id=t_a.id,
                data=TeacherAssignmentCreate(
                    class_id=c_1.id,
                    subject_id=s_arabic.id,
                    academic_year=academic_year
                )
            )
        assert exc_same_dup.value.status_code == 409
        assert "already assigned" in exc_same_dup.value.detail.lower()

        # Scenario 7: Edit assignment - Teacher A retains own assignment without triggering false duplicate error
        updated_self = teacher_service.update_assignment(
            assignment_id=assign_1.id,
            data=TeacherAssignmentUpdate(
                teacher_id=t_a.id,
                class_id=c_1.id,
                subject_id=s_arabic.id,
                academic_year=academic_year
            )
        )
        assert updated_self.id == assign_1.id

        # Scenario 8: Edit assignment - changing to already occupied (Class 1, Math has Teacher B)
        with pytest.raises(HTTPException) as exc_info_edit:
            teacher_service.update_assignment(
                assignment_id=assign_1.id,
                data=TeacherAssignmentUpdate(
                    teacher_id=t_a.id,
                    class_id=c_1.id,
                    subject_id=s_math.id,
                    academic_year=academic_year
                )
            )
        assert exc_info_edit.value.status_code == 409
        assert exc_info_edit.value.detail == "This subject is already assigned to another teacher in this class."

        # Scenario 9: Bulk assignment validation
        # Intra-batch duplicate to different teachers
        with pytest.raises(HTTPException) as exc_bulk_intra:
            teacher_service.bulk_assign(
                items=[
                    TeacherBulkAssignmentItem(teacher_id=t_a.id, class_id=c_2.id, subject_id=s_math.id, academic_year=academic_year),
                    TeacherBulkAssignmentItem(teacher_id=t_b.id, class_id=c_2.id, subject_id=s_math.id, academic_year=academic_year)
                ]
            )
        assert exc_bulk_intra.value.status_code == 409
        assert exc_bulk_intra.value.detail == "This subject is already assigned to another teacher in this class."

        # Bulk assignment with existing assignment conflict in DB
        with pytest.raises(HTTPException) as exc_bulk_db:
            teacher_service.bulk_assign(
                items=[
                    # c_1, s_arabic is already assigned to t_a, trying to assign to t_b
                    TeacherBulkAssignmentItem(teacher_id=t_b.id, class_id=c_1.id, subject_id=s_arabic.id, academic_year=academic_year)
                ]
            )
        assert exc_bulk_db.value.status_code == 409
        assert exc_bulk_db.value.detail == "This subject is already assigned to another teacher in this class."

        # Scenario 10: Academic year isolation
        # Same class & subject in a different academic year is ALLOWED for another teacher
        different_year = "2029-2030"
        assign_diff_year = teacher_service.assign_class_subject(
            teacher_id=t_b.id,
            data=TeacherAssignmentCreate(
                class_id=c_1.id,
                subject_id=s_arabic.id,
                academic_year=different_year
            )
        )
        assert assign_diff_year is not None
        assert assign_diff_year.teacher_id == t_b.id

        # Clean up different year assignment
        teacher_service.remove_assignment(assign_diff_year.id)

        # Scenario 11: ClassService enforcement
        class_service = ClassService(db_session)
        with pytest.raises(HTTPException) as exc_class_dup:
            class_service.assign_teacher_subject(
                class_id=c_1.id,
                teacher_id=t_b.id,
                subject_id=s_arabic.id,
                academic_year=academic_year
            )
        assert exc_class_dup.value.status_code == 409
        assert exc_class_dup.value.detail == "This subject is already assigned to another teacher in this class."

        # Scenario 12: SubjectService enforcement
        subject_service = SubjectService(db_session)
        from app.schemas.subject import SubjectAssignTeacherPayload
        with pytest.raises(HTTPException) as exc_subj_dup:
            subject_service.assign_teacher(
                subject_id=s_arabic.id,
                data=SubjectAssignTeacherPayload(
                    teacher_id=t_b.id,
                    class_id=c_1.id,
                    academic_year=academic_year
                )
            )
        assert exc_subj_dup.value.status_code == 409
        assert exc_subj_dup.value.detail == "This subject is already assigned to another teacher in this class."

    finally:
        # Cleanup test records
        db_session.query(TeacherAssignment).filter(
            TeacherAssignment.academic_year.in_([academic_year, academic_year.replace('-', '/')]),
            TeacherAssignment.class_id.in_([c_1.id, c_2.id])
        ).delete(synchronize_session=False)
        db_session.commit()
