from typing import Optional, List, Tuple
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_, case
from app.models.school_class import SchoolClass
from app.models.student_enrollment import StudentEnrollment
from app.models.student import Student
from app.models.teacher_assignment import TeacherAssignment
from app.models.teacher import Teacher
from app.models.subject import Subject
from app.models.timetable import Timetable
from app.models.exam import Exam
from app.repositories.base_repo import BaseRepository
from app.schemas.school_class import (
    ClassSummary,
    ClassCapacityMetrics,
    ClassEnrollmentStudent,
    ClassTeacherAssignmentItem,
    ClassSubjectItem,
    ClassTimetableItem,
    ClassExamItem
)


class ClassRepository(BaseRepository[SchoolClass]):
    """Repository for SchoolClass CRUD, statistics, and relational lookups."""

    def __init__(self, db: Session):
        super().__init__(SchoolClass, db)

    def get_by_code(self, code: str) -> Optional[SchoolClass]:
        return self.db.query(SchoolClass).filter(SchoolClass.code == code.upper().strip()).first()

    def get_by_identity(
        self,
        academic_year: str,
        division: str,
        level: str,
        section: Optional[str] = None,
        exclude_id: Optional[int] = None
    ) -> Optional[SchoolClass]:
        q = self.db.query(SchoolClass).filter(
            SchoolClass.academic_year == academic_year.strip(),
            SchoolClass.division == division.upper().strip(),
            func.lower(SchoolClass.level) == level.strip().lower()
        )
        if section and section.strip():
            q = q.filter(func.lower(SchoolClass.section) == section.strip().lower())
        else:
            q = q.filter(or_(SchoolClass.section.is_(None), SchoolClass.section == ""))

        if exclude_id is not None:
            q = q.filter(SchoolClass.id != exclude_id)
        return q.first()

    def get_by_name_section_year(self, name: str, section: Optional[str], academic_year: str, exclude_id: Optional[int] = None) -> Optional[SchoolClass]:
        q = self.db.query(SchoolClass).filter(
            func.lower(SchoolClass.name) == name.strip().lower(),
            SchoolClass.academic_year == academic_year.strip()
        )
        if section and section.strip():
            q = q.filter(func.lower(SchoolClass.section) == section.strip().lower())
        else:
            q = q.filter(or_(SchoolClass.section.is_(None), SchoolClass.section == ""))

        if exclude_id is not None:
            q = q.filter(SchoolClass.id != exclude_id)
        return q.first()

    def get_summary(self) -> ClassSummary:
        total = self.db.query(SchoolClass).count()
        active = self.db.query(SchoolClass).filter(SchoolClass.status == "ACTIVE").count()

        # Total students currently enrolled in active classes
        total_students_enrolled = (
            self.db.query(StudentEnrollment)
            .join(SchoolClass, StudentEnrollment.class_id == SchoolClass.id)
            .filter(
                StudentEnrollment.status == "ACTIVE",
                SchoolClass.status == "ACTIVE"
            )
            .count()
        )

        # Available seats across active classes
        active_classes = self.db.query(SchoolClass).filter(SchoolClass.status == "ACTIVE").all()
        available_seats = 0
        near_capacity_count = 0

        for c in active_classes:
            enrolled = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == c.id,
                StudentEnrollment.status == "ACTIVE"
            ).count()
            seats = max(0, c.capacity - enrolled)
            available_seats += seats
            if c.capacity > 0 and (enrolled / c.capacity) >= 0.90:
                near_capacity_count += 1

        return ClassSummary(
            total_classes=total,
            active_classes=active,
            total_students_enrolled=total_students_enrolled,
            available_seats=available_seats,
            near_capacity_classes=near_capacity_count
        )

    def get_active_classes_with_students(
        self,
        academic_year: Optional[str] = None,
        division: Optional[str] = None
    ) -> List[SchoolClass]:
        """
        CENTRAL BUSINESS RULE: Returns only classes that are:
        1. status == ACTIVE
        2. Have at least 1 active student enrollment

        Used universally by admin dropdowns, teacher portal, results management.
        Never returns empty classes, test classes, or inactive classes.
        """
        # Subquery: class_ids that have at least one active enrollment
        enrolled_class_ids_sq = (
            self.db.query(StudentEnrollment.class_id)
            .filter(StudentEnrollment.status == "ACTIVE")
        )

        if academic_year and academic_year.strip():
            y = academic_year.strip()
            y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]
            enrolled_class_ids_sq = enrolled_class_ids_sq.filter(
                StudentEnrollment.academic_year.in_(y_variants)
            )

        enrolled_class_ids = [r[0] for r in enrolled_class_ids_sq.distinct().all()]

        if not enrolled_class_ids:
            return []

        q = (
            self.db.query(SchoolClass)
            .filter(
                SchoolClass.status == "ACTIVE",
                SchoolClass.id.in_(enrolled_class_ids)
            )
        )


        if academic_year and academic_year.strip():
            y = academic_year.strip()
            y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]
            q = q.filter(SchoolClass.academic_year.in_(y_variants))

        if division and division.strip() and division.upper() != "ALL":
            q = q.filter(SchoolClass.division == division.upper().strip())

        division_order = case(
            (SchoolClass.division == "PRIMARY", 1),
            (SchoolClass.division == "SECONDARY", 2),
            else_=3
        )
        level_order = case(
            (SchoolClass.level == "Grade 1", 1),
            (SchoolClass.level == "Grade 2", 2),
            (SchoolClass.level == "Grade 3", 3),
            (SchoolClass.level == "Grade 4", 4),
            (SchoolClass.level == "Grade 5", 5),
            (SchoolClass.level == "Grade 6", 6),
            (SchoolClass.level == "Grade 7", 7),
            (SchoolClass.level == "Grade 8", 8),
            (SchoolClass.level == "Form 1", 9),
            (SchoolClass.level == "Form 2", 10),
            (SchoolClass.level == "Form 3", 11),
            (SchoolClass.level == "Form 4", 12),
            else_=99
        )

        classes = q.order_by(
            division_order.asc(),
            level_order.asc(),
            SchoolClass.section.asc()
        ).all()

        # Annotate with student counts
        for c in classes:
            c.students_count = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == c.id,
                StudentEnrollment.status == "ACTIVE"
            ).count()
            c.teachers_count = (
                self.db.query(TeacherAssignment.teacher_id)
                .filter(TeacherAssignment.class_id == c.id, TeacherAssignment.status == "ACTIVE")
                .distinct().count()
            )
            c.subjects_count = (
                self.db.query(TeacherAssignment.subject_id)
                .filter(TeacherAssignment.class_id == c.id, TeacherAssignment.status == "ACTIVE")
                .distinct().count()
            )
            c.available_seats = max(0, c.capacity - c.students_count)
            cap = max(1, c.capacity)
            c.utilization_rate = round((c.students_count / cap) * 100, 1)
            c.capacity_status = "NORMAL"

        return classes

    def search_classes(
        self,
        query: Optional[str] = None,
        academic_year: Optional[str] = None,
        division: Optional[str] = None,
        status: Optional[str] = None,
        level: Optional[str] = None,
        section: Optional[str] = None,
        capacity_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[SchoolClass], int]:
        q = self.db.query(SchoolClass)

        if query:
            pattern = f"%{query.strip()}%"
            q = q.filter(
                or_(
                    SchoolClass.name.ilike(pattern),
                    SchoolClass.code.ilike(pattern),
                    SchoolClass.level.ilike(pattern),
                    SchoolClass.section.ilike(pattern),
                    SchoolClass.academic_year.ilike(pattern)
                )
            )

        if academic_year and academic_year.strip():
            y = academic_year.strip()
            y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]
            q = q.filter(SchoolClass.academic_year.in_(y_variants))

        if division and division.strip() and division.upper().strip() != "ALL":
            q = q.filter(SchoolClass.division == division.upper().strip())

        if status and status.strip():
            q = q.filter(SchoolClass.status == status.upper().strip())

        if level and level.strip() and level.upper().strip() != "ALL":
            q = q.filter(or_(
                SchoolClass.level.ilike(f"{level.strip()}"),
                SchoolClass.name.ilike(f"%{level.strip()}%")
            ))

        if section and section.strip() and section.upper().strip() != "ALL":
            q = q.filter(SchoolClass.section.ilike(f"{section.strip()}"))

        division_order = case(
            (SchoolClass.division == "PRIMARY", 1),
            (SchoolClass.division == "SECONDARY", 2),
            else_=3
        )
        level_order = case(
            (SchoolClass.level == "Grade 1", 1),
            (SchoolClass.level == "Grade 2", 2),
            (SchoolClass.level == "Grade 3", 3),
            (SchoolClass.level == "Grade 4", 4),
            (SchoolClass.level == "Grade 5", 5),
            (SchoolClass.level == "Grade 6", 6),
            (SchoolClass.level == "Grade 7", 7),
            (SchoolClass.level == "Grade 8", 8),
            (SchoolClass.level == "Form 1", 9),
            (SchoolClass.level == "Form 2", 10),
            (SchoolClass.level == "Form 3", 11),
            (SchoolClass.level == "Form 4", 12),
            (SchoolClass.level == "Form 5", 13),
            (SchoolClass.level == "Form 6", 14),
            else_=99
        )

        total = q.count()
        classes = q.order_by(
            division_order.asc(),
            level_order.asc(),
            SchoolClass.section.asc(),
            SchoolClass.name.asc()
        ).offset(skip).limit(limit).all()

        # Compute dynamic counts & utilization for each class
        for c in classes:
            c.students_count = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == c.id,
                StudentEnrollment.status == "ACTIVE"
            ).count()

            # Unique teachers assigned to this class
            c.teachers_count = (
                self.db.query(TeacherAssignment.teacher_id)
                .filter(
                    TeacherAssignment.class_id == c.id,
                    TeacherAssignment.status == "ACTIVE"
                )
                .distinct()
                .count()
            )

            # Unique subjects assigned to this class
            c.subjects_count = (
                self.db.query(TeacherAssignment.subject_id)
                .filter(
                    TeacherAssignment.class_id == c.id,
                    TeacherAssignment.status == "ACTIVE"
                )
                .distinct()
                .count()
            )

            c.available_seats = max(0, c.capacity - c.students_count)
            cap = max(1, c.capacity)
            c.utilization_rate = round((c.students_count / cap) * 100, 1)

            if c.students_count > c.capacity:
                c.capacity_status = "OVER_CAPACITY"
            elif c.students_count == c.capacity:
                c.capacity_status = "FULL"
            elif c.utilization_rate >= 85.0:
                c.capacity_status = "NEAR_CAPACITY"
            else:
                c.capacity_status = "NORMAL"

        if capacity_filter and capacity_filter.strip():
            target_status = capacity_filter.upper().strip()
            classes = [c for c in classes if c.capacity_status == target_status]
            total = len(classes)

        return classes, total

    def get_class_capacity_metrics(self, c: SchoolClass) -> ClassCapacityMetrics:
        enrolled = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == c.id,
            StudentEnrollment.status == "ACTIVE"
        ).count()
        cap = max(1, c.capacity)
        available = max(0, c.capacity - enrolled)
        util_rate = round((enrolled / cap) * 100, 1)

        if enrolled > c.capacity:
            cap_status = "OVER_CAPACITY"
        elif enrolled == c.capacity:
            cap_status = "FULL"
        elif util_rate >= 85.0:
            cap_status = "NEAR_CAPACITY"
        else:
            cap_status = "NORMAL"

        return ClassCapacityMetrics(
            enrolled=enrolled,
            capacity=c.capacity,
            available_seats=available,
            utilization_rate=util_rate,
            capacity_status=cap_status
        )

    def get_class_students(self, class_id: int) -> List[ClassEnrollmentStudent]:
        enrollments = (
            self.db.query(StudentEnrollment)
            .filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.status == "ACTIVE"
            )
            .join(Student, StudentEnrollment.student_id == Student.id)
            .order_by(Student.last_name.asc(), Student.first_name.asc())
            .all()
        )

        items = []
        for e in enrollments:
            s = e.student
            if s:
                items.append(ClassEnrollmentStudent(
                    id=e.id,
                    student_id=s.id,
                    admission_number=s.admission_number,
                    full_name=s.full_name,
                    gender=s.gender,
                    status=s.status,
                    has_portal_access=s.user_id is not None,
                    enrollment_date=e.start_date or (s.created_at.date() if s.created_at else date.today()),
                    academic_year=e.academic_year
                ))
        return items

    def get_class_teachers(self, class_id: int) -> List[ClassTeacherAssignmentItem]:
        assignments = (
            self.db.query(TeacherAssignment)
            .filter(
                TeacherAssignment.class_id == class_id,
                TeacherAssignment.status == "ACTIVE"
            )
            .join(Teacher, TeacherAssignment.teacher_id == Teacher.id)
            .join(Subject, TeacherAssignment.subject_id == Subject.id)
            .order_by(Subject.name.asc())
            .all()
        )

        items = []
        for a in assignments:
            t = a.teacher
            sub = a.subject
            if t and sub:
                items.append(ClassTeacherAssignmentItem(
                    id=a.id,
                    teacher_id=t.id,
                    teacher_number=t.teacher_number,
                    full_name=t.full_name,
                    subject_id=sub.id,
                    subject_name=sub.name,
                    subject_code=sub.code,
                    academic_year=a.academic_year,
                    status=a.status
                ))
        return items

    def get_class_subjects(self, class_id: int) -> List[ClassSubjectItem]:
        assignments = (
            self.db.query(TeacherAssignment)
            .filter(
                TeacherAssignment.class_id == class_id,
                TeacherAssignment.status == "ACTIVE"
            )
            .all()
        )

        subject_map = {}
        for a in assignments:
            sub = a.subject
            t = a.teacher
            if sub:
                subject_map[sub.id] = ClassSubjectItem(
                    id=sub.id,
                    code=sub.code,
                    name=sub.name,
                    department=sub.department,
                    teacher_id=t.id if t else None,
                    teacher_name=t.full_name if t else None,
                    status="ACTIVE"
                )
        return list(subject_map.values())

    def get_class_timetables(self, class_id: int) -> List[ClassTimetableItem]:
        slots = (
            self.db.query(Timetable)
            .filter(
                Timetable.class_id == class_id,
                Timetable.status == "ACTIVE"
            )
            .join(Subject, Timetable.subject_id == Subject.id)
            .outerjoin(Teacher, Timetable.teacher_id == Teacher.id)
            .order_by(Timetable.day_of_week.asc(), Timetable.start_time.asc())
            .all()
        )

        items = []
        for s in slots:
            sub = s.subject
            t = s.teacher
            items.append(ClassTimetableItem(
                id=s.id,
                day_of_week=s.day_of_week,
                start_time=s.start_time,
                end_time=s.end_time,
                subject_name=sub.name if sub else "Unknown Subject",
                subject_code=sub.code if sub else "",
                teacher_name=t.full_name if t else None,
                room=s.room,
                status=s.status
            ))
        return items

    def get_class_exams(self, class_id: int) -> List[ClassExamItem]:
        exams = (
            self.db.query(Exam)
            .filter(Exam.class_id == class_id)
            .order_by(Exam.start_date.desc())
            .all()
        )

        items = []
        for ex in exams:
            items.append(ClassExamItem(
                id=ex.id,
                name=ex.name,
                exam_type=ex.exam_type,
                academic_year=ex.academic_year,
                start_date=ex.start_date,
                end_date=ex.end_date,
                status=ex.status
            ))
        return items
