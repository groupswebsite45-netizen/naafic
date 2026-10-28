from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_
from app.models.subject import Subject
from app.models.teacher_assignment import TeacherAssignment
from app.models.teacher import Teacher
from app.models.school_class import SchoolClass
from app.models.student_enrollment import StudentEnrollment
from app.models.timetable import Timetable
from app.models.exam import Exam
from app.repositories.base_repo import BaseRepository
from app.schemas.subject import (
    SubjectSummary,
    SubjectClassAssignmentItem,
    SubjectTeacherAssignmentItem,
    SubjectTimetableItem,
    SubjectExamItem
)


class SubjectRepository(BaseRepository[Subject]):
    """Repository for Subject database operations and relational counts."""

    def __init__(self, db: Session):
        super().__init__(Subject, db)

    def get_by_code(self, code: str) -> Optional[Subject]:
        return self.db.query(Subject).filter(Subject.code == code.upper().strip()).first()

    def get_distinct_departments(self) -> List[str]:
        results = (
            self.db.query(Subject.department)
            .filter(Subject.department.isnot(None), Subject.department != "")
            .distinct()
            .order_by(Subject.department.asc())
            .all()
        )
        return [r[0] for r in results if r[0]]

    def get_summary(self) -> SubjectSummary:
        total = self.db.query(Subject).count()
        active = self.db.query(Subject).filter(Subject.status == "ACTIVE").count()

        # Assigned subjects: subjects that have at least one active assignment in teacher_assignments
        assigned_subquery = (
            self.db.query(TeacherAssignment.subject_id)
            .filter(TeacherAssignment.status == "ACTIVE")
            .distinct()
            .scalar_subquery()
        )
        assigned_count = self.db.query(Subject).filter(Subject.id.in_(assigned_subquery)).count()
        unassigned_count = self.db.query(Subject).filter(Subject.id.notin_(assigned_subquery)).count()

        # Distinct departments count
        departments_count = (
            self.db.query(Subject.department)
            .filter(Subject.department.isnot(None), Subject.department != "")
            .distinct()
            .count()
        )

        return SubjectSummary(
            total_subjects=total,
            active_subjects=active,
            assigned_subjects=assigned_count,
            unassigned_subjects=unassigned_count,
            departments_count=departments_count
        )

    def search_subjects(
        self,
        query: Optional[str] = None,
        division: Optional[str] = None,
        level: Optional[str] = None,
        class_id: Optional[int] = None,
        department: Optional[str] = None,
        status: Optional[str] = None,
        assigned_filter: Optional[str] = None,
        academic_year: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Subject], int]:
        q = self.db.query(Subject)

        if class_id:
            target_class = self.db.query(SchoolClass).filter(SchoolClass.id == class_id).first()
            if target_class:
                class_div = (target_class.division or "PRIMARY").upper().strip()
                class_lvl = (target_class.level or target_class.name).strip()
                q = q.filter(Subject.division.in_([class_div, "ALL"]))
                # If level is configured on subject, match level or NULL
                q = q.filter(
                    or_(
                        Subject.applicable_levels.is_(None),
                        Subject.applicable_levels == "",
                        Subject.applicable_levels.ilike(f"%{class_lvl}%")
                    )
                )

        if division and division.strip() and division.upper().strip() != "ALL":
            q = q.filter(Subject.division.in_([division.upper().strip(), "ALL"]))

        if level and level.strip() and level.upper().strip() != "ALL":
            q = q.filter(
                or_(
                    Subject.applicable_levels.is_(None),
                    Subject.applicable_levels == "",
                    Subject.applicable_levels.ilike(f"%{level.strip()}%")
                )
            )

        if query:
            pattern = f"%{query.strip()}%"
            q = q.filter(
                or_(
                    Subject.name.ilike(pattern),
                    Subject.code.ilike(pattern),
                    Subject.department.ilike(pattern)
                )
            )

        if department and department.strip():
            q = q.filter(Subject.department == department.strip())

        if status and status.strip():
            q = q.filter(Subject.status == status.upper().strip())

        if academic_year and academic_year.strip():
            year_subquery = (
                self.db.query(TeacherAssignment.subject_id)
                .filter(
                    TeacherAssignment.academic_year == academic_year.strip(),
                    TeacherAssignment.status == "ACTIVE"
                )
                .distinct()
                .scalar_subquery()
            )
            q = q.filter(Subject.id.in_(year_subquery))

        if assigned_filter and assigned_filter.strip():
            assigned_subquery = (
                self.db.query(TeacherAssignment.subject_id)
                .filter(TeacherAssignment.status == "ACTIVE")
                .distinct()
                .scalar_subquery()
            )
            if assigned_filter.upper().strip() == "ASSIGNED":
                q = q.filter(Subject.id.in_(assigned_subquery))
            elif assigned_filter.upper().strip() == "UNASSIGNED":
                q = q.filter(Subject.id.notin_(assigned_subquery))

        total = q.count()
        subjects = q.order_by(Subject.name.asc()).offset(skip).limit(limit).all()

        # Dynamically compute relational counts for each subject
        for s in subjects:
            s.classes_count = (
                self.db.query(TeacherAssignment.class_id)
                .filter(
                    TeacherAssignment.subject_id == s.id,
                    TeacherAssignment.status == "ACTIVE"
                )
                .distinct()
                .count()
            )
            s.teachers_count = (
                self.db.query(TeacherAssignment.teacher_id)
                .filter(
                    TeacherAssignment.subject_id == s.id,
                    TeacherAssignment.status == "ACTIVE"
                )
                .distinct()
                .count()
            )
            s.timetables_count = (
                self.db.query(Timetable)
                .filter(
                    Timetable.subject_id == s.id,
                    Timetable.status == "ACTIVE"
                )
                .count()
            )
            s.exams_count = (
                self.db.query(Exam)
                .filter(Exam.subject_id == s.id)
                .count()
            )

        return subjects, total

    def get_subject_classes(self, subject_id: int) -> List[SubjectClassAssignmentItem]:
        assignments = (
            self.db.query(TeacherAssignment)
            .filter(
                TeacherAssignment.subject_id == subject_id,
                TeacherAssignment.status == "ACTIVE"
            )
            .join(SchoolClass, TeacherAssignment.class_id == SchoolClass.id)
            .outerjoin(Teacher, TeacherAssignment.teacher_id == Teacher.id)
            .order_by(SchoolClass.name.asc())
            .all()
        )

        items = []
        for a in assignments:
            c = a.school_class
            t = a.teacher
            if c:
                students_count = self.db.query(StudentEnrollment).filter(
                    StudentEnrollment.class_id == c.id,
                    StudentEnrollment.status == "ACTIVE"
                ).count()

                items.append(SubjectClassAssignmentItem(
                    id=a.id,
                    class_id=c.id,
                    class_name=c.name,
                    class_code=c.code,
                    section=c.section,
                    academic_year=a.academic_year,
                    teacher_id=t.id if t else None,
                    teacher_name=t.full_name if t else None,
                    students_count=students_count,
                    status=a.status
                ))
        return items

    def get_subject_teachers(self, subject_id: int) -> List[SubjectTeacherAssignmentItem]:
        assignments = (
            self.db.query(TeacherAssignment)
            .filter(
                TeacherAssignment.subject_id == subject_id,
                TeacherAssignment.status == "ACTIVE"
            )
            .join(Teacher, TeacherAssignment.teacher_id == Teacher.id)
            .join(SchoolClass, TeacherAssignment.class_id == SchoolClass.id)
            .order_by(Teacher.last_name.asc(), Teacher.first_name.asc())
            .all()
        )

        items = []
        for a in assignments:
            t = a.teacher
            c = a.school_class
            if t and c:
                items.append(SubjectTeacherAssignmentItem(
                    id=a.id,
                    teacher_id=t.id,
                    teacher_number=t.teacher_number,
                    full_name=t.full_name,
                    class_id=c.id,
                    class_name=c.name,
                    academic_year=a.academic_year,
                    status=a.status
                ))
        return items

    def get_subject_timetables(self, subject_id: int) -> List[SubjectTimetableItem]:
        slots = (
            self.db.query(Timetable)
            .filter(
                Timetable.subject_id == subject_id,
                Timetable.status == "ACTIVE"
            )
            .join(SchoolClass, Timetable.class_id == SchoolClass.id)
            .outerjoin(Teacher, Timetable.teacher_id == Teacher.id)
            .order_by(Timetable.day_of_week.asc(), Timetable.start_time.asc())
            .all()
        )

        items = []
        for slot in slots:
            c = slot.school_class
            t = slot.teacher
            items.append(SubjectTimetableItem(
                id=slot.id,
                day_of_week=slot.day_of_week,
                start_time=slot.start_time,
                end_time=slot.end_time,
                class_name=c.name if c else "Unknown Class",
                class_code=c.code if c else "",
                teacher_name=t.full_name if t else None,
                room=slot.room,
                status=slot.status
            ))
        return items

    def get_subject_exams(self, subject_id: int) -> List[SubjectExamItem]:
        exams = (
            self.db.query(Exam)
            .filter(Exam.subject_id == subject_id)
            .join(SchoolClass, Exam.class_id == SchoolClass.id)
            .order_by(Exam.start_date.desc())
            .all()
        )

        items = []
        for ex in exams:
            c = ex.school_class
            items.append(SubjectExamItem(
                id=ex.id,
                name=ex.name,
                exam_type=ex.exam_type,
                class_name=c.name if c else "Unknown Class",
                academic_year=ex.academic_year,
                start_date=ex.start_date,
                max_marks=float(ex.max_marks),
                status=ex.status
            ))
        return items
