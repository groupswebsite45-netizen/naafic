from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.timetable import Timetable
from app.repositories.base_repo import BaseRepository
from app.schemas.teacher import TeacherSummary


class TeacherRepository(BaseRepository[Teacher]):
    """Repository for Teacher database operations."""

    def __init__(self, db: Session):
        super().__init__(Teacher, db)

    def get_by_number(self, teacher_number: str) -> Optional[Teacher]:
        return self.db.query(Teacher).filter(Teacher.teacher_number == teacher_number.upper().strip()).first()

    def get_by_email(self, email: str) -> Optional[Teacher]:
        return self.db.query(Teacher).filter(Teacher.email == email.lower().strip()).first()

    def get_by_user_id(self, user_id: int) -> Optional[Teacher]:
        return self.db.query(Teacher).filter(Teacher.user_id == user_id).first()

    def search_teachers(
        self,
        query: Optional[str] = None,
        status: Optional[str] = None,
        class_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        has_portal: Optional[bool] = None,
        academic_year: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Teacher], int]:
        q = self.db.query(Teacher)

        if query:
            pattern = f"%{query.strip()}%"
            q = q.filter(
                or_(
                    Teacher.first_name.ilike(pattern),
                    Teacher.last_name.ilike(pattern),
                    Teacher.teacher_number.ilike(pattern),
                    Teacher.email.ilike(pattern),
                    Teacher.phone.ilike(pattern),
                    Teacher.qualification.ilike(pattern)
                )
            )

        if status:
            q = q.filter(Teacher.status == status.upper().strip())

        if has_portal is not None:
            if has_portal:
                q = q.filter(Teacher.user_id.isnot(None))
            else:
                q = q.filter(Teacher.user_id.is_(None))

        if class_id or subject_id or academic_year:
            q = q.join(TeacherAssignment, Teacher.id == TeacherAssignment.teacher_id)
            if class_id:
                q = q.filter(TeacherAssignment.class_id == class_id)
            if subject_id:
                q = q.filter(TeacherAssignment.subject_id == subject_id)
            if academic_year:
                q = q.filter(TeacherAssignment.academic_year == academic_year.strip())
            q = q.distinct()

        total = q.count()
        teachers = q.order_by(Teacher.first_name.asc()).offset(skip).limit(limit).all()
        for t in teachers:
            t.has_portal_access = t.user_id is not None
        return teachers, total

    def get_summary(self) -> TeacherSummary:
        total = self.db.query(Teacher).count()
        active = self.db.query(Teacher).filter(Teacher.status == "ACTIVE").count()
        inactive = self.db.query(Teacher).filter(Teacher.status != "ACTIVE").count()

        # Teachers without any active assignments
        assigned_subquery = (
            self.db.query(TeacherAssignment.teacher_id)
            .filter(TeacherAssignment.status == "ACTIVE")
            .distinct()
            .scalar_subquery()
        )
        unassigned = self.db.query(Teacher).filter(Teacher.id.notin_(assigned_subquery)).count()

        return TeacherSummary(
            total_teachers=total,
            active_teachers=active,
            inactive_teachers=inactive,
            unassigned_teachers=unassigned
        )

    def assign_to_class_subject(
        self,
        teacher_id: int,
        class_id: int,
        subject_id: int,
        academic_year: str
    ) -> TeacherAssignment:
        year_str = academic_year.strip()
        year_variants = {year_str, year_str.replace('/', '-'), year_str.replace('-', '/')}
        existing = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.class_id == class_id,
            TeacherAssignment.subject_id == subject_id,
            TeacherAssignment.academic_year.in_(year_variants),
            TeacherAssignment.status == "ACTIVE"
        ).first()

        if existing:
            if existing.teacher_id != teacher_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This subject is already assigned to another teacher in this class."
                )
            return existing

        assignment = TeacherAssignment(
            teacher_id=teacher_id,
            class_id=class_id,
            subject_id=subject_id,
            academic_year=year_str,
            status="ACTIVE"
        )
        try:
            self.db.add(assignment)
            self.db.commit()
            self.db.refresh(assignment)
            return assignment
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This subject is already assigned to another teacher in this class."
            )

    def remove_assignment(self, assignment_id: int) -> bool:
        a = self.db.query(TeacherAssignment).filter(TeacherAssignment.id == assignment_id).first()
        if a:
            self.db.delete(a)
            self.db.commit()
            return True
        return False

    def get_teacher_assignments(self, teacher_id: int) -> List[TeacherAssignment]:
        return self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher_id,
            TeacherAssignment.status == "ACTIVE"
        ).all()

    def get_teacher_timetables(self, teacher_id: int) -> List[Timetable]:
        return self.db.query(Timetable).filter(
            Timetable.teacher_id == teacher_id,
            Timetable.status == "ACTIVE"
        ).all()
