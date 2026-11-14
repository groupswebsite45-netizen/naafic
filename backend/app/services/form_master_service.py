from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.user import User
from app.models.teacher import Teacher
from app.models.school_class import SchoolClass
from app.models.student_enrollment import StudentEnrollment
from app.models.form_master import FormMasterAssignment
from app.repositories.form_master_repo import FormMasterRepository
from app.schemas.form_master import (
    FormMasterAppointPayload,
    FormMasterReplacePayload,
    FormMasterRevokePayload,
    FormMasterAssignmentResponse,
    ClassFormMasterItem,
    AvailableTeacherItem,
    FormMasterAdminOverview,
)


class FormMasterAdminService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FormMasterRepository(db)

    def _get_default_academic_year(self) -> str:
        # Check active class or latest academic year
        latest_class = self.db.query(SchoolClass).order_by(SchoolClass.academic_year.desc()).first()
        if latest_class:
            return latest_class.academic_year
        return "2026/2027"

    def get_overview(self, academic_year: Optional[str] = None) -> FormMasterAdminOverview:
        year = academic_year or self._get_default_academic_year()
        total_classes = self.db.query(SchoolClass).filter(
            SchoolClass.status == "ACTIVE",
            SchoolClass.academic_year == year
        ).count()

        active_assignments = self.repo.get_all_active_assignments(academic_year=year)
        assigned_class_ids = {a.class_id for a in active_assignments}
        assigned_count = len(assigned_class_ids)
        unassigned_count = max(0, total_classes - assigned_count)
        distinct_teachers = len({a.teacher_id for a in active_assignments})

        return FormMasterAdminOverview(
            total_classes=total_classes,
            assigned_classes_count=assigned_count,
            unassigned_classes_count=unassigned_count,
            total_form_masters=distinct_teachers,
            academic_year=year
        )

    def list_classes_with_form_masters(
        self,
        academic_year: Optional[str] = None,
        division: Optional[str] = None,
        status_filter: Optional[str] = None  # "ASSIGNED", "UNASSIGNED", or None
    ) -> List[ClassFormMasterItem]:
        year = academic_year or self._get_default_academic_year()
        query = self.db.query(SchoolClass).filter(
            SchoolClass.status == "ACTIVE",
            SchoolClass.academic_year == year
        )
        if division and division != "ALL":
            query = query.filter(SchoolClass.division == division.upper())

        classes = query.order_by(SchoolClass.division, SchoolClass.level, SchoolClass.section, SchoolClass.name).all()

        active_assignments = self.repo.get_all_active_assignments(academic_year=year)
        assignment_by_class: Dict[int, FormMasterAssignment] = {a.class_id: a for a in active_assignments}

        # Student counts per class
        student_counts = dict(
            self.db.query(
                StudentEnrollment.class_id,
                func.count(StudentEnrollment.id)
            )
            .filter(
                StudentEnrollment.academic_year == year,
                StudentEnrollment.status == "ACTIVE"
            )
            .group_by(StudentEnrollment.class_id)
            .all()
        )

        results: List[ClassFormMasterItem] = []
        for c in classes:
            assignment = assignment_by_class.get(c.id)
            is_assigned = assignment is not None

            if status_filter == "ASSIGNED" and not is_assigned:
                continue
            if status_filter == "UNASSIGNED" and is_assigned:
                continue

            results.append(
                ClassFormMasterItem(
                    class_id=c.id,
                    class_name=c.name,
                    class_code=c.code,
                    division=c.division,
                    level=c.level,
                    section=c.section,
                    academic_year=c.academic_year,
                    capacity=c.capacity or 40,
                    student_count=student_counts.get(c.id, 0),
                    assignment_id=assignment.id if assignment else None,
                    form_master_id=assignment.teacher_id if assignment else None,
                    form_master_name=assignment.teacher_name if assignment else None,
                    form_master_number=assignment.teacher_number if assignment else None,
                    form_master_email=assignment.teacher_email if assignment else None,
                    form_master_phone=assignment.teacher_phone if assignment else None,
                    status="ASSIGNED" if is_assigned else "UNASSIGNED",
                    appointed_at=assignment.appointed_at if assignment else None,
                    notes=assignment.notes if assignment else None
                )
            )

        return results

    def list_available_teachers(self, academic_year: Optional[str] = None) -> List[AvailableTeacherItem]:
        year = academic_year or self._get_default_academic_year()
        teachers = (
            self.db.query(Teacher)
            .filter(Teacher.status == "ACTIVE")
            .order_by(Teacher.first_name, Teacher.last_name)
            .all()
        )

        active_assignments = self.repo.get_all_active_assignments(academic_year=year)
        teacher_assignments_map: Dict[int, List[FormMasterAssignment]] = {}
        for a in active_assignments:
            teacher_assignments_map.setdefault(a.teacher_id, []).append(a)

        items: List[AvailableTeacherItem] = []
        for t in teachers:
            assigned = teacher_assignments_map.get(t.id, [])
            count = len(assigned)
            items.append(
                AvailableTeacherItem(
                    teacher_id=t.id,
                    teacher_number=t.teacher_number,
                    full_name=t.full_name,
                    email=t.email,
                    phone=t.phone,
                    gender=t.gender,
                    active_form_classes_count=count,
                    can_assign=count < 2,
                    assigned_classes=[a.class_name for a in assigned]
                )
            )

        return items

    def appoint_form_master(
        self, payload: FormMasterAppointPayload, admin_user: User
    ) -> List[FormMasterAssignmentResponse]:
        # 1. Validate Teacher
        teacher = self.db.query(Teacher).filter(Teacher.id == payload.teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teacher with ID {payload.teacher_id} does not exist."
            )
        if teacher.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Teacher {teacher.full_name} is currently {teacher.status} and cannot be appointed."
            )

        # 2. Validate class count and duplicates
        if len(payload.class_ids) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one class must be selected for appointment."
            )
        if len(payload.class_ids) > 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A teacher can supervise at most two classes as Form Master."
            )
        if len(set(payload.class_ids)) != len(payload.class_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate class selections are not allowed."
            )

        # 3. Check teacher's current active load
        current_active = self.repo.get_active_assignments_for_teacher(teacher.id, academic_year=payload.academic_year)
        if len(current_active) + len(payload.class_ids) > 2:
            already_assigned_classes = [a.class_name for a in current_active]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Teacher {teacher.full_name} already supervises {len(current_active)} class(es) "
                    f"({', '.join(already_assigned_classes)}). Maximum allowed is 2 classes per teacher."
                )
            )

        # 4. Check each class
        created_assignments = []
        for class_id in payload.class_ids:
            school_class = self.db.query(SchoolClass).filter(SchoolClass.id == class_id).first()
            if not school_class:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Class with ID {class_id} does not exist."
                )
            if school_class.status != "ACTIVE":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Class {school_class.name} is not ACTIVE."
                )

            # Check if class already has an active Form Master
            existing_active = self.repo.get_active_assignment_for_class(class_id, academic_year=payload.academic_year)
            if existing_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Class '{school_class.name}' is already assigned to Form Master "
                        f"'{existing_active.teacher_name}' for academic year {payload.academic_year}. "
                        "Please replace or revoke the existing appointment first."
                    )
                )

            # Create assignment
            assignment = self.repo.create(
                teacher_id=teacher.id,
                class_id=class_id,
                academic_year=payload.academic_year,
                appointed_by_id=admin_user.id,
                notes=payload.notes
            )
            created_assignments.append(assignment)

        return [FormMasterAssignmentResponse.model_validate(a) for a in created_assignments]

    def replace_form_master(
        self, assignment_id: int, payload: FormMasterReplacePayload, admin_user: User
    ) -> FormMasterAssignmentResponse:
        assignment = self.repo.get_by_id(assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Form Master assignment with ID {assignment_id} not found."
            )
        if assignment.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only ACTIVE assignments can be replaced."
            )

        if assignment.teacher_id == payload.new_teacher_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The replacement teacher is already the Form Master for this assignment."
            )

        new_teacher = self.db.query(Teacher).filter(Teacher.id == payload.new_teacher_id).first()
        if not new_teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teacher with ID {payload.new_teacher_id} does not exist."
            )
        if new_teacher.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Teacher {new_teacher.full_name} is currently {new_teacher.status}."
            )

        # Check new teacher's load
        new_teacher_active = self.repo.get_active_assignments_for_teacher(new_teacher.id, academic_year=assignment.academic_year)
        if len(new_teacher_active) >= 2:
            already = [a.class_name for a in new_teacher_active]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Teacher {new_teacher.full_name} already supervises 2 classes "
                    f"({', '.join(already)}) and cannot take another class."
                )
            )

        # Revoke old assignment
        old_teacher_name = assignment.teacher_name
        self.repo.revoke(
            assignment,
            revoked_by_id=admin_user.id,
            notes=f"Replaced by {new_teacher.full_name}. {payload.notes or ''}".strip()
        )

        # Create new assignment
        new_assignment = self.repo.create(
            teacher_id=new_teacher.id,
            class_id=assignment.class_id,
            academic_year=assignment.academic_year,
            appointed_by_id=admin_user.id,
            notes=f"Replaced {old_teacher_name}. {payload.notes or ''}".strip()
        )

        return FormMasterAssignmentResponse.model_validate(new_assignment)

    def revoke_form_master(
        self, assignment_id: int, payload: FormMasterRevokePayload, admin_user: User
    ) -> FormMasterAssignmentResponse:
        assignment = self.repo.get_by_id(assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Form Master assignment with ID {assignment_id} not found."
            )
        if assignment.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Assignment is already {assignment.status}."
            )

        revoked = self.repo.revoke(
            assignment,
            revoked_by_id=admin_user.id,
            notes=payload.notes
        )
        return FormMasterAssignmentResponse.model_validate(revoked)

    def get_assignment(self, assignment_id: int) -> FormMasterAssignmentResponse:
        assignment = self.repo.get_by_id(assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found."
            )
        return FormMasterAssignmentResponse.model_validate(assignment)

