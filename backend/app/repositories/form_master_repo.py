from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.form_master import FormMasterAssignment
from app.models.school_class import SchoolClass
from app.models.teacher import Teacher


class FormMasterRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, assignment_id: int) -> Optional[FormMasterAssignment]:
        return self.db.query(FormMasterAssignment).filter(FormMasterAssignment.id == assignment_id).first()

    def get_active_assignment_for_class(self, class_id: int, academic_year: str) -> Optional[FormMasterAssignment]:
        return (
            self.db.query(FormMasterAssignment)
            .filter(
                FormMasterAssignment.class_id == class_id,
                FormMasterAssignment.academic_year == academic_year,
                FormMasterAssignment.status == "ACTIVE"
            )
            .first()
        )

    def get_active_assignments_for_teacher(
        self, teacher_id: int, academic_year: Optional[str] = None
    ) -> List[FormMasterAssignment]:
        query = self.db.query(FormMasterAssignment).filter(
            FormMasterAssignment.teacher_id == teacher_id,
            FormMasterAssignment.status == "ACTIVE"
        )
        if academic_year:
            query = query.filter(FormMasterAssignment.academic_year == academic_year)
        return query.all()

    def get_all_active_assignments(self, academic_year: Optional[str] = None) -> List[FormMasterAssignment]:
        query = self.db.query(FormMasterAssignment).filter(FormMasterAssignment.status == "ACTIVE")
        if academic_year:
            query = query.filter(FormMasterAssignment.academic_year == academic_year)
        return query.all()

    def list_assignments(
        self,
        academic_year: Optional[str] = None,
        status: Optional[str] = None,
        teacher_id: Optional[int] = None,
        class_id: Optional[int] = None
    ) -> List[FormMasterAssignment]:
        query = self.db.query(FormMasterAssignment)
        if academic_year:
            query = query.filter(FormMasterAssignment.academic_year == academic_year)
        if status:
            query = query.filter(FormMasterAssignment.status == status)
        if teacher_id:
            query = query.filter(FormMasterAssignment.teacher_id == teacher_id)
        if class_id:
            query = query.filter(FormMasterAssignment.class_id == class_id)
        return query.order_by(FormMasterAssignment.appointed_at.desc()).all()

    def create(
        self,
        teacher_id: int,
        class_id: int,
        academic_year: str,
        appointed_by_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> FormMasterAssignment:
        assignment = FormMasterAssignment(
            teacher_id=teacher_id,
            class_id=class_id,
            academic_year=academic_year,
            status="ACTIVE",
            notes=notes,
            appointed_by_id=appointed_by_id,
            appointed_at=datetime.now(timezone.utc)
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def revoke(
        self,
        assignment: FormMasterAssignment,
        revoked_by_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> FormMasterAssignment:
        assignment.status = "REVOKED"
        assignment.revoked_by_id = revoked_by_id
        assignment.revoked_at = datetime.now(timezone.utc)
        if notes:
            assignment.notes = f"{assignment.notes or ''} [Revocation: {notes}]".strip()
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

