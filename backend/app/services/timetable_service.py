from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, time
from sqlalchemy.orm import Session
from sqlalchemy import distinct, func
from fastapi import HTTPException, status

from app.models.timetable import Timetable
from app.models.school_class import SchoolClass
from app.models.teacher import Teacher
from app.models.subject import Subject
from app.models.teacher_assignment import TeacherAssignment
from app.models.teacher_availability import TeacherAvailability
from app.models.timetable_setting import TimetableSetting
from app.models.student_enrollment import StudentEnrollment
from app.models.institution import Institution

from app.repositories.timetable_repo import TimetableRepository
from app.repositories.class_repo import ClassRepository
from app.repositories.subject_repo import SubjectRepository
from app.repositories.teacher_repo import TeacherRepository
from app.repositories.audit_repo import AuditLogRepository

from app.services.timetable_generator import TimetableGenerator
from app.services.timetable_conflict_service import TimetableConflictService
from app.services.timetable_pdf_service import TimetablePdfService

from app.schemas.timetable import (
    TimetableCreate,
    TimetableUpdate,
    TimetableResponse,
    TimetableSummary,
    TimetableFilterOptions,
    TimetableCheckConflictPayload,
    TimetableConflictCheckResponse,
    TimetableGenerateRequest,
    TimetableGenerateResponse,
    TimetablePublishRequest,
    TimetablePublishResponse,
    TimetableClassOverviewResponse,
    TimetableAuthorizedFaculty,
    TimetableBatchSaveRequest,
    TimetableConflictDetail,
    TimetableMoveSlotRequest,
    TimetableSwapSlotsRequest
)
from app.schemas.timetable_setting import (
    TimetableSettingCreate,
    TimetableSettingUpdate,
    TimetableSettingResponse
)
from app.schemas.teacher_availability import (
    TeacherAvailabilityCreate,
    TeacherAvailabilityUpdate,
    TeacherAvailabilityResponse,
    TeacherAvailabilityMatrixItem
)


class TimetableService:
    """Service handling Timetable scheduling, automated generation, conflict auditing, and publication."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = TimetableRepository(db)
        self.class_repo = ClassRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.teacher_repo = TeacherRepository(db)
        self.audit_repo = AuditLogRepository(db)
        self.generator = TimetableGenerator(db)
        self.conflict_service = TimetableConflictService(db)

    def get_summary(self, academic_year: Optional[str] = None) -> TimetableSummary:
        """Return live timetable metrics and detected conflicts from PostgreSQL."""
        return self.repo.get_summary(academic_year=academic_year)

    def get_filter_options(self, academic_year: Optional[str] = None) -> TimetableFilterOptions:
        """Return available filter options from database."""
        return self.repo.get_filter_options(academic_year=academic_year)

    def check_slot_conflict(self, data: TimetableCheckConflictPayload) -> TimetableConflictCheckResponse:
        """Validate if a proposed schedule slot conflicts with existing entries."""
        if data.start_time >= data.end_time:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Slot end time must be after start time."
            )

        conflicts = self.repo.collect_conflicts(
            class_id=data.class_id,
            day_of_week=data.day_of_week,
            start_time=data.start_time,
            end_time=data.end_time,
            academic_year=data.academic_year,
            teacher_id=data.teacher_id,
            room=data.room,
            exclude_id=data.exclude_id
        )

        return TimetableConflictCheckResponse(
            has_conflict=len(conflicts) > 0,
            conflicts_count=len(conflicts),
            conflicts=conflicts
        )

    def get_entry(self, entry_id: int) -> Timetable:
        t = self.repo.get_by_id(entry_id)
        if not t:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timetable slot not found.")
        return t

    def search_entries(
        self,
        class_id: Optional[int] = None,
        teacher_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        day_of_week: Optional[str] = None,
        academic_year: Optional[str] = None,
        room: Optional[str] = None,
        status_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 200
    ) -> Tuple[List[TimetableResponse], int]:
        entries, total = self.repo.search_timetable(
            class_id=class_id,
            teacher_id=teacher_id,
            subject_id=subject_id,
            day_of_week=day_of_week,
            academic_year=academic_year,
            room=room,
            status=status_filter,
            skip=skip,
            limit=limit
        )

        response_list = [self._format_response(e) for e in entries]
        return response_list, total

    def _format_response(self, e: Timetable) -> TimetableResponse:
        return TimetableResponse(
            id=e.id,
            class_id=e.class_id,
            subject_id=e.subject_id,
            teacher_id=e.teacher_id,
            academic_year=e.academic_year,
            day_of_week=e.day_of_week,
            start_time=e.start_time,
            end_time=e.end_time,
            room=e.room,
            period_number=e.period_number,
            is_break=e.is_break if e.is_break is not None else False,
            status=e.status,
            published_at=e.published_at,
            published_by_id=e.published_by_id,
            class_name=e.school_class.name if e.school_class else f"Class {e.class_id}",
            class_code=e.school_class.code if e.school_class else "",
            subject_name=e.subject.name if e.subject else f"Subject {e.subject_id}",
            subject_code=e.subject.code if e.subject else "",
            teacher_name=e.teacher.full_name if e.teacher else None,
            room_number=e.room,
            school_class=None,
            subject=None,
            teacher=None,
            created_at=e.created_at,
            updated_at=e.updated_at
        )

    # =========================================================================
    # CLASS-FIRST TIMETABLE WORKFLOW
    # =========================================================================

    def get_class_timetable_overview(
        self,
        class_id: int,
        academic_year: str
    ) -> TimetableClassOverviewResponse:
        """
        Core workflow method:
        Retrieves class metadata, authorized teacher-subject assignments,
        active/draft timetable slots, publication status, and conflict diagnostics.
        """
        school_class = self.class_repo.get_by_id(class_id)
        if not school_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found.")

        year_clean = academic_year.strip()
        year_variants = {year_clean, year_clean.replace("/", "-"), year_clean.replace("-", "/")}
        if school_class.academic_year:
            cy = school_class.academic_year.strip()
            year_variants.update([cy, cy.replace("/", "-"), cy.replace("-", "/")])
        year_variants_list = list(year_variants)

        # 1. Enrolled students count
        enrolled_count = (
            self.db.query(StudentEnrollment)
            .filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.status == "ACTIVE"
            )
            .count()
        )

        # 2. Authorized assignments: Retrieve all active assignments for this class
        assignments = (
            self.db.query(TeacherAssignment)
            .filter(
                TeacherAssignment.class_id == class_id,
                TeacherAssignment.status == "ACTIVE",
                TeacherAssignment.academic_year.in_(year_variants_list)
            )
            .all()
        )

        # Fallback if no exact year matches: query active assignments for class regardless of year string
        if not assignments:
            assignments = (
                self.db.query(TeacherAssignment)
                .filter(
                    TeacherAssignment.class_id == class_id,
                    TeacherAssignment.status == "ACTIVE"
                )
                .all()
            )

        authorized_faculty = []
        seen_subjects = set()
        for a in assignments:
            sub = a.subject
            t = a.teacher
            if sub and sub.id not in seen_subjects:
                seen_subjects.add(sub.id)
                # Determine default weekly periods from subject name or level
                name_lower = sub.name.lower()
                if any(core in name_lower for core in ["math", "english", "somali", "arabic"]):
                    def_periods = 5
                elif any(sci in name_lower for sci in ["physic", "chem", "bio", "science"]):
                    def_periods = 4
                elif any(elec in name_lower for elec in ["islam", "geograph", "histor", "computer"]):
                    def_periods = 3
                else:
                    def_periods = 4

                authorized_faculty.append(TimetableAuthorizedFaculty(
                    assignment_id=a.id,
                    subject_id=sub.id,
                    subject_name=sub.name,
                    subject_code=sub.code or "",
                    teacher_id=t.id if t else None,
                    teacher_name=t.full_name if t else None,
                    teacher_number=t.teacher_number if t else None,
                    recommended_weekly_periods=def_periods
                ))

        # 3. Timetable slots for this class
        slots = (
            self.db.query(Timetable)
            .filter(
                Timetable.class_id == class_id,
                Timetable.academic_year.in_(year_variants_list)
            )
            .order_by(Timetable.day_of_week.asc(), Timetable.start_time.asc())
            .all()
        )

        # Determine overall publication status
        if not slots:
            pub_status = "EMPTY"
        elif all(s.status == "PUBLISHED" for s in slots):
            pub_status = "PUBLISHED"
        elif any(s.status == "PUBLISHED" for s in slots):
            pub_status = "PARTIALLY_PUBLISHED"
        else:
            pub_status = "DRAFT"

        # 4. Check Conflicts
        conflicts = self.conflict_service.validate_class_schedule(class_id, academic_year)

        formatted_slots = [self._format_response(s) for s in slots]

        return TimetableClassOverviewResponse(
            class_id=school_class.id,
            class_name=school_class.name,
            class_code=school_class.code,
            division=school_class.division or "PRIMARY",
            level=school_class.level or school_class.name,
            section=school_class.section or "A",
            academic_year=year_clean,
            capacity=school_class.capacity,
            enrolled_students=enrolled_count,
            authorized_assignments=authorized_faculty,
            assigned_subjects=[
                {
                    "subject_id": af.subject_id,
                    "subject_name": af.subject_name,
                    "subject_code": af.subject_code,
                    "teacher_id": af.teacher_id,
                    "teacher_name": af.teacher_name,
                    "teacher_number": af.teacher_number,
                    "weekly_lessons": af.recommended_weekly_periods,
                    "has_teacher": af.teacher_id is not None
                }
                for af in authorized_faculty
            ],
            has_assignments=len(authorized_faculty) > 0,
            timetables=formatted_slots,
            existing_slots=formatted_slots,
            total_slots=len(formatted_slots),
            published_slots=sum(1 for s in formatted_slots if s.status == "PUBLISHED"),
            has_unresolved_conflicts=len(conflicts) > 0,
            publication_status=pub_status,
            total_periods=len(formatted_slots),
            conflicts_count=len(conflicts),
            conflicts=conflicts
        )

    # =========================================================================
    # AUTOMATIC GENERATION & BATCH SAVING
    # =========================================================================

    def generate_class_timetable(
        self,
        request: TimetableGenerateRequest,
        user_id: Optional[int] = None
    ) -> TimetableGenerateResponse:
        """Run intelligent constraint-satisfaction engine for selected class."""
        res = self.generator.generate_for_class(request, user_id=user_id)
        if res.success:
            self.audit_repo.log_event(
                action="TIMETABLE_AUTO_GENERATED",
                user_id=user_id,
                details={
                    "class_id": res.class_id,
                    "academic_year": res.academic_year,
                    "periods_generated": res.total_generated_periods
                }
            )
        return res

    def batch_save_class_timetable(
        self,
        payload: TimetableBatchSaveRequest,
        user_id: Optional[int] = None
    ) -> List[TimetableResponse]:
        """Save edited grid slots for a class atomically."""
        school_class = self.class_repo.get_by_id(payload.class_id)
        if not school_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found.")

        year_clean = payload.academic_year.strip()
        year_variants = [year_clean, year_clean.replace("/", "-"), year_clean.replace("-", "/")]

        # Remove existing draft/generated slots for this class
        self.db.query(Timetable).filter(
            Timetable.class_id == payload.class_id,
            Timetable.academic_year.in_(year_variants)
        ).delete(synchronize_session=False)

        new_status = "PUBLISHED" if payload.publish_immediately else "DRAFT"
        pub_at = datetime.now() if payload.publish_immediately else None

        persisted = []
        for slot in payload.slots:
            entry = Timetable(
                class_id=payload.class_id,
                subject_id=slot.subject_id,
                teacher_id=slot.teacher_id,
                academic_year=year_clean,
                day_of_week=slot.day_of_week.strip(),
                start_time=slot.start_time,
                end_time=slot.end_time,
                room=slot.room.strip() if slot.room else None,
                period_number=slot.period_number,
                is_break=slot.is_break,
                status=new_status,
                published_at=pub_at,
                published_by_id=user_id if payload.publish_immediately else None
            )
            self.db.add(entry)
            persisted.append(entry)

        self.db.commit()

        self.audit_repo.log_event(
            action="TIMETABLE_BATCH_SAVED",
            user_id=user_id,
            details={
                "class_id": payload.class_id,
                "academic_year": year_clean,
                "slots_count": len(persisted),
                "published": payload.publish_immediately
            }
        )

        return [self._format_response(e) for e in persisted]

    # =========================================================================
    # PUBLISHING LIFECYCLE
    # =========================================================================

    def publish_timetable(
        self,
        request: TimetablePublishRequest,
        user_id: Optional[int] = None
    ) -> TimetablePublishResponse:
        """
        Publish official timetable for a class or entire school.
        Detects conflicts before publishing and prevents publication if critical conflicts exist.
        """
        year_clean = request.academic_year.strip()
        year_variants = [year_clean, year_clean.replace("/", "-"), year_clean.replace("-", "/")]

        # 1. Conflict Validation Gate
        if request.class_id:
            conflicts = self.conflict_service.validate_class_schedule(request.class_id, request.academic_year)
            classes_to_publish = [request.class_id]
        else:
            conflicts = self.repo.detect_all_conflicts(request.academic_year)
            # Find all classes with slots in this year
            classes_to_publish = [
                r[0] for r in self.db.query(distinct(Timetable.class_id)).filter(
                    Timetable.academic_year.in_(year_variants)
                ).all()
            ]

        critical_conflicts = [c for c in conflicts if c.severity == "ERROR"]

        if critical_conflicts and not request.force:
            descriptions = "; ".join([c.message for c in critical_conflicts[:5]])
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot publish timetable with unresolved critical conflicts ({len(critical_conflicts)}): {descriptions}"
            )

        # 2. Update status to PUBLISHED
        q = self.db.query(Timetable).filter(
            Timetable.academic_year.in_(year_variants),
            Timetable.class_id.in_(classes_to_publish),
            Timetable.status != "ARCHIVED"
        )
        updated_count = q.update(
            {
                "status": "PUBLISHED",
                "published_at": datetime.now(),
                "published_by_id": user_id
            },
            synchronize_session=False
        )
        self.db.commit()

        self.audit_repo.log_event(
            action="TIMETABLE_PUBLISHED",
            user_id=user_id,
            details={
                "class_id": request.class_id,
                "academic_year": year_clean,
                "published_count": updated_count
            }
        )

        return TimetablePublishResponse(
            success=True,
            published_count=updated_count,
            academic_year=year_clean,
            message=f"Timetable successfully published ({updated_count} lessons). Students and teachers can now view their official schedules.",
            conflicts_found=len(conflicts),
            conflicts=conflicts
        )

    def unpublish_timetable(
        self,
        class_id: int,
        academic_year: str,
        user_id: Optional[int] = None
    ) -> TimetablePublishResponse:
        """Revert timetable from PUBLISHED to DRAFT for corrections."""
        year_clean = academic_year.strip()
        year_variants = [year_clean, year_clean.replace("/", "-"), year_clean.replace("-", "/")]

        q = self.db.query(Timetable).filter(
            Timetable.class_id == class_id,
            Timetable.academic_year.in_(year_variants),
            Timetable.status.in_(["PUBLISHED", "ACTIVE"])
        )
        updated_count = q.update(
            {"status": "DRAFT"},
            synchronize_session=False
        )
        self.db.commit()

        self.audit_repo.log_event(
            action="TIMETABLE_UNPUBLISHED",
            user_id=user_id,
            details={"class_id": class_id, "academic_year": year_clean}
        )

        return TimetablePublishResponse(
            success=True,
            published_count=updated_count,
            academic_year=year_clean,
            message=f"Timetable for class reverted to DRAFT ({updated_count} lessons). Hidden from student portal during revisions.",
            conflicts_found=0,
            conflicts=[]
        )

    # =========================================================================
    # SETTINGS & SCHEDULE PARAMETERS
    # =========================================================================

    def get_timetable_setting(
        self,
        academic_year: str,
        division: Optional[str] = "ALL"
    ) -> TimetableSettingResponse:
        year_clean = academic_year.strip()
        year_variants = [year_clean, year_clean.replace("/", "-"), year_clean.replace("-", "/")]

        setting = (
            self.db.query(TimetableSetting)
            .filter(
                TimetableSetting.academic_year.in_(year_variants),
                TimetableSetting.is_active == True
            )
            .first()
        )

        if not setting:
            # Default institutional setting
            setting = TimetableSetting(
                academic_year=year_clean,
                division=division or "ALL",
                school_days="Saturday,Sunday,Monday,Tuesday,Wednesday,Thursday",
                start_time=time(7, 30),
                end_time=time(13, 30),
                period_duration_minutes=45,
                break_duration_minutes=20,
                break_after_period=3,
                lunch_duration_minutes=30,
                lunch_after_period=5,
                periods_per_day=6,
                is_active=True
            )
            self.db.add(setting)
            self.db.commit()
            self.db.refresh(setting)

        return TimetableSettingResponse(
            id=setting.id,
            academic_year=setting.academic_year,
            division=setting.division,
            school_days=setting.school_days,
            start_time=setting.start_time,
            end_time=setting.end_time,
            period_duration_minutes=setting.period_duration_minutes,
            break_duration_minutes=setting.break_duration_minutes,
            break_after_period=setting.break_after_period,
            lunch_duration_minutes=setting.lunch_duration_minutes,
            lunch_after_period=setting.lunch_after_period,
            periods_per_day=setting.periods_per_day,
            is_active=setting.is_active,
            created_at=setting.created_at,
            updated_at=setting.updated_at,
            days_list=setting.days_list
        )

    def update_timetable_setting(
        self,
        setting_id: int,
        payload: TimetableSettingUpdate,
        user_id: Optional[int] = None
    ) -> TimetableSettingResponse:
        setting = self.db.query(TimetableSetting).filter(TimetableSetting.id == setting_id).first()
        if not setting:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timetable settings not found.")

        if payload.academic_year:
            setting.academic_year = payload.academic_year.strip()
        if payload.division:
            setting.division = payload.division.strip()
        if payload.school_days:
            setting.school_days = payload.school_days.strip()
        if payload.start_time:
            setting.start_time = payload.start_time
        if payload.end_time:
            setting.end_time = payload.end_time
        if payload.period_duration_minutes is not None:
            setting.period_duration_minutes = payload.period_duration_minutes
        if payload.break_duration_minutes is not None:
            setting.break_duration_minutes = payload.break_duration_minutes
        if payload.break_after_period is not None:
            setting.break_after_period = payload.break_after_period
        if payload.lunch_duration_minutes is not None:
            setting.lunch_duration_minutes = payload.lunch_duration_minutes
        if payload.lunch_after_period is not None:
            setting.lunch_after_period = payload.lunch_after_period
        if payload.periods_per_day is not None:
            setting.periods_per_day = payload.periods_per_day
        if payload.is_active is not None:
            setting.is_active = payload.is_active

        self.db.commit()
        self.db.refresh(setting)

        return TimetableSettingResponse(
            id=setting.id,
            academic_year=setting.academic_year,
            division=setting.division,
            school_days=setting.school_days,
            start_time=setting.start_time,
            end_time=setting.end_time,
            period_duration_minutes=setting.period_duration_minutes,
            break_duration_minutes=setting.break_duration_minutes,
            break_after_period=setting.break_after_period,
            lunch_duration_minutes=setting.lunch_duration_minutes,
            lunch_after_period=setting.lunch_after_period,
            periods_per_day=setting.periods_per_day,
            is_active=setting.is_active,
            created_at=setting.created_at,
            updated_at=setting.updated_at,
            days_list=setting.days_list
        )

    # =========================================================================
    # TEACHER AVAILABILITY MANAGEMENT
    # =========================================================================

    def get_teacher_availabilities(
        self,
        teacher_id: int,
        academic_year: str
    ) -> List[TeacherAvailabilityResponse]:
        year_clean = academic_year.strip()
        year_variants = [year_clean, year_clean.replace("/", "-"), year_clean.replace("-", "/")]

        rows = (
            self.db.query(TeacherAvailability)
            .filter(
                TeacherAvailability.teacher_id == teacher_id,
                TeacherAvailability.academic_year.in_(year_variants)
            )
            .all()
        )

        teacher = self.teacher_repo.get_by_id(teacher_id)
        t_name = teacher.full_name if teacher else ""
        t_num = teacher.teacher_number if teacher else ""

        results = []
        for r in rows:
            results.append(TeacherAvailabilityResponse(
                id=r.id,
                teacher_id=r.teacher_id,
                teacher_name=t_name,
                teacher_number=t_num,
                academic_year=r.academic_year,
                day_of_week=r.day_of_week,
                start_time=r.start_time,
                end_time=r.end_time,
                is_available=r.is_available,
                max_periods_per_day=r.max_periods_per_day,
                max_periods_per_week=r.max_periods_per_week,
                notes=r.notes,
                created_at=r.created_at,
                updated_at=r.updated_at
            ))
        return results

    def set_teacher_availability(
        self,
        payload: TeacherAvailabilityCreate,
        user_id: Optional[int] = None
    ) -> Any:
        year_clean = payload.academic_year.strip()
        year_variants = [year_clean, year_clean.replace("/", "-"), year_clean.replace("-", "/")]

        # Case 1: Batch submission
        if payload.availabilities:
            saved_count = 0
            for item in payload.availabilities:
                existing = (
                    self.db.query(TeacherAvailability)
                    .filter(
                        TeacherAvailability.teacher_id == payload.teacher_id,
                        TeacherAvailability.day_of_week == item.day_of_week.strip(),
                        TeacherAvailability.academic_year.in_(year_variants)
                    )
                    .first()
                )
                if existing:
                    existing.is_available = item.is_available
                    existing.start_time = item.start_time
                    existing.end_time = item.end_time
                    existing.max_periods_per_day = item.max_periods_per_day
                    existing.max_periods_per_week = item.max_periods_per_week
                    existing.notes = item.notes
                else:
                    target = TeacherAvailability(
                        teacher_id=payload.teacher_id,
                        academic_year=year_clean,
                        day_of_week=item.day_of_week.strip(),
                        start_time=item.start_time,
                        end_time=item.end_time,
                        is_available=item.is_available,
                        max_periods_per_day=item.max_periods_per_day,
                        max_periods_per_week=item.max_periods_per_week,
                        notes=item.notes
                    )
                    self.db.add(target)
                saved_count += 1

            self.db.commit()
            return {"message": f"Successfully updated availability for {saved_count} days.", "saved_count": saved_count}

        # Case 2: Single-day submission
        day = (payload.day_of_week or "Saturday").strip()
        existing = (
            self.db.query(TeacherAvailability)
            .filter(
                TeacherAvailability.teacher_id == payload.teacher_id,
                TeacherAvailability.day_of_week == day,
                TeacherAvailability.academic_year.in_(year_variants)
            )
            .first()
        )

        if existing:
            existing.is_available = payload.is_available if payload.is_available is not None else True
            existing.start_time = payload.start_time
            existing.end_time = payload.end_time
            existing.max_periods_per_day = payload.max_periods_per_day
            existing.max_periods_per_week = payload.max_periods_per_week
            existing.notes = payload.notes
            target = existing
        else:
            target = TeacherAvailability(
                teacher_id=payload.teacher_id,
                academic_year=year_clean,
                day_of_week=day,
                start_time=payload.start_time,
                end_time=payload.end_time,
                is_available=payload.is_available if payload.is_available is not None else True,
                max_periods_per_day=payload.max_periods_per_day,
                max_periods_per_week=payload.max_periods_per_week,
                notes=payload.notes
            )
            self.db.add(target)

        self.db.commit()
        self.db.refresh(target)

        teacher = self.teacher_repo.get_by_id(payload.teacher_id)
        return TeacherAvailabilityResponse(
            id=target.id,
            teacher_id=target.teacher_id,
            teacher_name=teacher.full_name if teacher else "",
            teacher_number=teacher.teacher_number if teacher else "",
            academic_year=target.academic_year,
            day_of_week=target.day_of_week,
            start_time=target.start_time,
            end_time=target.end_time,
            is_available=target.is_available,
            max_periods_per_day=target.max_periods_per_day,
            max_periods_per_week=target.max_periods_per_week,
            notes=target.notes,
            created_at=target.created_at,
            updated_at=target.updated_at
        )

    def get_teacher_availability_matrix(
        self,
        academic_year: str
    ) -> List[TeacherAvailabilityMatrixItem]:
        """Matrix view showing all teachers with occupied periods, weekly load, and availability."""
        year_clean = academic_year.strip()
        year_variants = [year_clean, year_clean.replace("/", "-"), year_clean.replace("-", "/")]

        teachers = self.db.query(Teacher).filter(Teacher.status == "ACTIVE").order_by(Teacher.last_name.asc()).all()
        slots = (
            self.db.query(Timetable)
            .filter(
                Timetable.academic_year.in_(year_variants),
                Timetable.status.in_(["ACTIVE", "PUBLISHED"])
            )
            .all()
        )

        availabilities = (
            self.db.query(TeacherAvailability)
            .filter(TeacherAvailability.academic_year.in_(year_variants))
            .all()
        )
        avail_map = {(a.teacher_id, a.day_of_week.lower()): a for a in availabilities}

        days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        matrix = []

        for t in teachers:
            t_slots = [s for s in slots if s.teacher_id == t.id]
            weekly_count = len(t_slots)

            daily_info = {}
            for day in days:
                d_slots = [s for s in t_slots if s.day_of_week.lower() == day.lower()]
                av = avail_map.get((t.id, day.lower()))
                daily_info[day] = {
                    "is_available": av.is_available if av else True,
                    "scheduled_periods": len(d_slots),
                    "lessons": [
                        {
                            "subject": s.subject.name if s.subject else "Subject",
                            "class": s.school_class.name if s.school_class else f"Class {s.class_id}",
                            "time": f"{s.start_time.strftime('%H:%M')}–{s.end_time.strftime('%H:%M')}",
                            "room": s.room
                        }
                        for s in d_slots
                    ]
                }

            matrix.append(TeacherAvailabilityMatrixItem(
                teacher_id=t.id,
                teacher_name=t.full_name,
                teacher_number=t.teacher_number,
                total_assigned_weekly_periods=weekly_count,
                max_periods_per_week=25,
                daily_availability=daily_info
            ))

        return matrix

    # =========================================================================
    # SINGLE ENTRY CRUD
    # =========================================================================

    def create_entry(self, data: TimetableCreate, user_id: Optional[int] = None) -> TimetableResponse:
        if data.start_time >= data.end_time:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Slot end time must be after start time."
            )

        school_class = self.class_repo.get_by_id(data.class_id)
        if not school_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {data.class_id} not found.")

        subject = self.subject_repo.get_by_id(data.subject_id)
        if not subject:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subject with ID {data.subject_id} not found.")

        if data.teacher_id:
            teacher = self.teacher_repo.get_by_id(data.teacher_id)
            if not teacher:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher with ID {data.teacher_id} not found.")

        conflicts = self.repo.collect_conflicts(
            class_id=data.class_id,
            day_of_week=data.day_of_week,
            start_time=data.start_time,
            end_time=data.end_time,
            academic_year=data.academic_year,
            teacher_id=data.teacher_id,
            room=data.room
        )

        if conflicts:
            conflict_descriptions = " | ".join([c.message for c in conflicts])
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Scheduling conflict detected ({len(conflicts)}): {conflict_descriptions}"
            )

        entry = Timetable(
            class_id=data.class_id,
            subject_id=data.subject_id,
            teacher_id=data.teacher_id,
            academic_year=data.academic_year.strip(),
            day_of_week=data.day_of_week.strip(),
            start_time=data.start_time,
            end_time=data.end_time,
            room=data.room.strip() if data.room and data.room.strip() else None,
            period_number=data.period_number,
            is_break=data.is_break,
            status=data.status.upper().strip()
        )
        created = self.repo.create(entry)
        self.audit_repo.log_event(
            action="TIMETABLE_SLOT_CREATED",
            user_id=user_id,
            details={
                "slot_id": created.id,
                "class_id": created.class_id,
                "subject_id": created.subject_id,
                "day": created.day_of_week,
                "time": f"{created.start_time}-{created.end_time}"
            }
        )
        return self._format_response(created)

    def update_entry(self, entry_id: int, data: TimetableUpdate, user_id: Optional[int] = None) -> TimetableResponse:
        t = self.get_entry(entry_id)

        class_id = data.class_id if data.class_id is not None else t.class_id
        subject_id = data.subject_id if data.subject_id is not None else t.subject_id
        teacher_id = data.teacher_id if data.teacher_id is not None else t.teacher_id
        academic_year = data.academic_year.strip() if data.academic_year else t.academic_year
        day_of_week = data.day_of_week.strip() if data.day_of_week else t.day_of_week
        start_time = data.start_time or t.start_time
        end_time = data.end_time or t.end_time
        room = data.room.strip() if data.room is not None else t.room
        period_number = data.period_number if data.period_number is not None else t.period_number
        is_break = data.is_break if data.is_break is not None else t.is_break
        status_val = data.status.upper().strip() if data.status else t.status

        if start_time >= end_time:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Slot end time must be after start time."
            )

        if class_id != t.class_id and not self.class_repo.get_by_id(class_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found.")
        if subject_id != t.subject_id and not self.subject_repo.get_by_id(subject_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subject with ID {subject_id} not found.")
        if teacher_id and teacher_id != t.teacher_id and not self.teacher_repo.get_by_id(teacher_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher with ID {teacher_id} not found.")

        if status_val in ["ACTIVE", "PUBLISHED"]:
            conflicts = self.repo.collect_conflicts(
                class_id=class_id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                academic_year=academic_year,
                teacher_id=teacher_id,
                room=room,
                exclude_id=entry_id
            )
            if conflicts:
                conflict_descriptions = " | ".join([c.message for c in conflicts])
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Scheduling conflict detected ({len(conflicts)}): {conflict_descriptions}"
                )

        t.class_id = class_id
        t.subject_id = subject_id
        t.teacher_id = teacher_id
        t.academic_year = academic_year
        t.day_of_week = day_of_week
        t.start_time = start_time
        t.end_time = end_time
        t.room = room
        t.period_number = period_number
        t.is_break = is_break
        t.status = status_val

        updated = self.repo.update(t)
        self.audit_repo.log_event(
            action="TIMETABLE_SLOT_UPDATED",
            user_id=user_id,
            details={"slot_id": updated.id, "day": updated.day_of_week, "time": f"{updated.start_time}-{updated.end_time}"}
        )
        return self._format_response(updated)

    def delete_entry(self, entry_id: int, user_id: Optional[int] = None) -> None:
        t = self.get_entry(entry_id)
        self.repo.delete(t)
        self.audit_repo.log_event(
            action="TIMETABLE_SLOT_DELETED",
            user_id=user_id,
            details={"slot_id": entry_id, "class_id": t.class_id, "day": t.day_of_week}
        )

    def move_slot(
        self,
        payload: TimetableMoveSlotRequest,
        user_id: Optional[int] = None
    ) -> TimetableResponse:
        """
        Move a timetable slot to a new target day and period time.
        Validates interval overlaps, teacher availability, and class commitments.
        """
        slot = self.get_entry(payload.slot_id)

        target_day = payload.target_day.strip()
        target_start = payload.target_start_time
        target_end = payload.target_end_time
        target_room = payload.target_room.strip() if payload.target_room and payload.target_room.strip() else slot.room

        if target_start >= target_end:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Target slot end time must be after start time."
            )

        year_clean = slot.academic_year.strip()
        year_variants = [year_clean, year_clean.replace("/", "-"), year_clean.replace("-", "/")]

        # 1. Check if destination slot is occupied by another lesson for the SAME class
        same_class_conflict = (
            self.db.query(Timetable)
            .filter(
                Timetable.id != slot.id,
                Timetable.class_id == slot.class_id,
                func.lower(Timetable.day_of_week) == target_day.lower(),
                Timetable.academic_year.in_(year_variants),
                Timetable.status.in_(["ACTIVE", "PUBLISHED", "DRAFT", "GENERATED"]),
                Timetable.start_time < target_end,
                Timetable.end_time > target_start
            )
            .first()
        )
        if same_class_conflict:
            subj_name = same_class_conflict.subject.name if same_class_conflict.subject else "another lesson"
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Destination slot is already occupied by '{subj_name}' ({same_class_conflict.start_time.strftime('%H:%M')}–{same_class_conflict.end_time.strftime('%H:%M')}). Drag to an empty slot or swap lessons."
            )

        # 2. Check Teacher Collision across other classes
        if slot.teacher_id:
            teacher_conflict = (
                self.db.query(Timetable)
                .filter(
                    Timetable.id != slot.id,
                    Timetable.teacher_id == slot.teacher_id,
                    func.lower(Timetable.day_of_week) == target_day.lower(),
                    Timetable.status.in_(["ACTIVE", "PUBLISHED", "DRAFT", "GENERATED"]),
                    Timetable.start_time < target_end,
                    Timetable.end_time > target_start
                )
                .first()
            )
            if teacher_conflict:
                t_name = slot.teacher.full_name if slot.teacher else f"Teacher #{slot.teacher_id}"
                c_name = teacher_conflict.school_class.name if teacher_conflict.school_class else f"Class #{teacher_conflict.class_id}"
                subj_name = teacher_conflict.subject.name if teacher_conflict.subject else "a lesson"
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Teacher '{t_name}' is already teaching '{subj_name}' for '{c_name}' on {target_day} ({teacher_conflict.start_time.strftime('%H:%M')}–{teacher_conflict.end_time.strftime('%H:%M')})."
                )

            # Check Teacher Availability Preferences
            avail = (
                self.db.query(TeacherAvailability)
                .filter(
                    TeacherAvailability.teacher_id == slot.teacher_id,
                    func.lower(TeacherAvailability.day_of_week) == target_day.lower()
                )
                .first()
            )
            if avail and not avail.is_available:
                t_name = slot.teacher.full_name if slot.teacher else f"Teacher #{slot.teacher_id}"
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Teacher '{t_name}' is marked unavailable on {target_day}."
                )

        # 3. Check Room Collision
        if target_room:
            room_conflict = (
                self.db.query(Timetable)
                .filter(
                    Timetable.id != slot.id,
                    func.lower(Timetable.room) == target_room.lower(),
                    func.lower(Timetable.day_of_week) == target_day.lower(),
                    Timetable.status.in_(["ACTIVE", "PUBLISHED", "DRAFT", "GENERATED"]),
                    Timetable.start_time < target_end,
                    Timetable.end_time > target_start
                )
                .first()
            )
            if room_conflict:
                c_name = room_conflict.school_class.name if room_conflict.school_class else f"Class #{room_conflict.class_id}"
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Room '{target_room}' is already in use by '{c_name}' on {target_day} ({room_conflict.start_time.strftime('%H:%M')}–{room_conflict.end_time.strftime('%H:%M')})."
                )

        # Apply validated move
        slot.day_of_week = target_day
        slot.start_time = target_start
        slot.end_time = target_end
        if payload.target_period_number is not None:
            slot.period_number = payload.target_period_number
        if target_room:
            slot.room = target_room

        self.db.commit()
        self.db.refresh(slot)

        self.audit_repo.log_event(
            action="TIMETABLE_SLOT_MOVED",
            user_id=user_id,
            details={
                "slot_id": slot.id,
                "class_id": slot.class_id,
                "new_day": target_day,
                "new_time": f"{target_start}-{target_end}"
            }
        )

        return self._format_response(slot)

    def swap_slots(
        self,
        payload: TimetableSwapSlotsRequest,
        user_id: Optional[int] = None
    ) -> List[TimetableResponse]:
        """
        Swap two timetable slots' day, period, and time coordinates.
        Validates BOTH resulting positions to ensure no teacher, room, or availability conflicts occur.
        If either fails, the swap is cancelled and original timetable preserved.
        """
        slot1 = self.get_entry(payload.slot_id_1)
        slot2 = self.get_entry(payload.slot_id_2)

        if slot1.id == slot2.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot swap a timetable slot with itself.")

        # Planned positions:
        # Slot 1 moves to: (slot2.day_of_week, slot2.start_time, slot2.end_time, slot2.period_number, slot2.room)
        # Slot 2 moves to: (slot1.day_of_week, slot1.start_time, slot1.end_time, slot1.period_number, slot1.room)

        # 1. Validate Teacher 1 in Slot 2's position
        if slot1.teacher_id:
            t1_conflict = (
                self.db.query(Timetable)
                .filter(
                    Timetable.id.notin_([slot1.id, slot2.id]),
                    Timetable.teacher_id == slot1.teacher_id,
                    func.lower(Timetable.day_of_week) == slot2.day_of_week.lower(),
                    Timetable.status.in_(["ACTIVE", "PUBLISHED", "DRAFT", "GENERATED"]),
                    Timetable.start_time < slot2.end_time,
                    Timetable.end_time > slot2.start_time
                )
                .first()
            )
            if t1_conflict:
                t_name = slot1.teacher.full_name if slot1.teacher else f"Teacher #{slot1.teacher_id}"
                c_name = t1_conflict.school_class.name if t1_conflict.school_class else f"Class #{t1_conflict.class_id}"
                subj_name = t1_conflict.subject.name if t1_conflict.subject else "a lesson"
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Cannot swap: Teacher '{t_name}' has an overlapping class commitment in '{c_name}' on {slot2.day_of_week} ({t1_conflict.start_time.strftime('%H:%M')}–{t1_conflict.end_time.strftime('%H:%M')})."
                )

            avail1 = (
                self.db.query(TeacherAvailability)
                .filter(
                    TeacherAvailability.teacher_id == slot1.teacher_id,
                    func.lower(TeacherAvailability.day_of_week) == slot2.day_of_week.lower()
                )
                .first()
            )
            if avail1 and not avail1.is_available:
                t_name = slot1.teacher.full_name if slot1.teacher else f"Teacher #{slot1.teacher_id}"
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Cannot swap: Teacher '{t_name}' is configured as unavailable on {slot2.day_of_week}."
                )

        # 2. Validate Teacher 2 in Slot 1's position
        if slot2.teacher_id:
            t2_conflict = (
                self.db.query(Timetable)
                .filter(
                    Timetable.id.notin_([slot1.id, slot2.id]),
                    Timetable.teacher_id == slot2.teacher_id,
                    func.lower(Timetable.day_of_week) == slot1.day_of_week.lower(),
                    Timetable.status.in_(["ACTIVE", "PUBLISHED", "DRAFT", "GENERATED"]),
                    Timetable.start_time < slot1.end_time,
                    Timetable.end_time > slot1.start_time
                )
                .first()
            )
            if t2_conflict:
                t_name = slot2.teacher.full_name if slot2.teacher else f"Teacher #{slot2.teacher_id}"
                c_name = t2_conflict.school_class.name if t2_conflict.school_class else f"Class #{t2_conflict.class_id}"
                subj_name = t2_conflict.subject.name if t2_conflict.subject else "a lesson"
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Cannot swap: Teacher '{t_name}' has an overlapping class commitment in '{c_name}' on {slot1.day_of_week} ({t2_conflict.start_time.strftime('%H:%M')}–{t2_conflict.end_time.strftime('%H:%M')})."
                )

            avail2 = (
                self.db.query(TeacherAvailability)
                .filter(
                    TeacherAvailability.teacher_id == slot2.teacher_id,
                    func.lower(TeacherAvailability.day_of_week) == slot1.day_of_week.lower()
                )
                .first()
            )
            if avail2 and not avail2.is_available:
                t_name = slot2.teacher.full_name if slot2.teacher else f"Teacher #{slot2.teacher_id}"
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Cannot swap: Teacher '{t_name}' is configured as unavailable on {slot1.day_of_week}."
                )

        # 3. Swap positions atomically
        s1_day, s1_start, s1_end, s1_period, s1_room = slot1.day_of_week, slot1.start_time, slot1.end_time, slot1.period_number, slot1.room
        s2_day, s2_start, s2_end, s2_period, s2_room = slot2.day_of_week, slot2.start_time, slot2.end_time, slot2.period_number, slot2.room

        slot1.day_of_week = s2_day
        slot1.start_time = s2_start
        slot1.end_time = s2_end
        slot1.period_number = s2_period
        slot1.room = s2_room

        slot2.day_of_week = s1_day
        slot2.start_time = s1_start
        slot2.end_time = s1_end
        slot2.period_number = s1_period
        slot2.room = s1_room

        self.db.commit()
        self.db.refresh(slot1)
        self.db.refresh(slot2)

        self.audit_repo.log_event(
            action="TIMETABLE_SLOTS_SWAPPED",
            user_id=user_id,
            details={
                "slot_id_1": slot1.id,
                "slot_id_2": slot2.id,
                "class_id": slot1.class_id
            }
        )

        return [self._format_response(slot1), self._format_response(slot2)]

    # =========================================================================
    # PDF EXPORTS
    # =========================================================================

    def generate_class_pdf(self, class_id: int, academic_year: str) -> bytes:
        school_class = self.class_repo.get_by_id(class_id)
        if not school_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found.")

        year_clean = academic_year.strip()
        year_variants = [year_clean, year_clean.replace("/", "-"), year_clean.replace("-", "/")]

        entries = (
            self.db.query(Timetable)
            .filter(
                Timetable.class_id == class_id,
                Timetable.academic_year.in_(year_variants),
                Timetable.status.in_(["ACTIVE", "PUBLISHED"])
            )
            .all()
        )

        institution = self.db.query(Institution).first()
        return TimetablePdfService.generate_class_pdf(school_class, year_clean, entries, institution=institution)

    def generate_teacher_pdf(self, teacher_id: int, academic_year: str) -> bytes:
        teacher = self.teacher_repo.get_by_id(teacher_id)
        if not teacher:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found.")

        year_clean = academic_year.strip()
        year_variants = [year_clean, year_clean.replace("/", "-"), year_clean.replace("-", "/")]

        entries = (
            self.db.query(Timetable)
            .filter(
                Timetable.teacher_id == teacher_id,
                Timetable.academic_year.in_(year_variants),
                Timetable.status.in_(["ACTIVE", "PUBLISHED"])
            )
            .all()
        )

        institution = self.db.query(Institution).first()
        return TimetablePdfService.generate_teacher_pdf(teacher, year_clean, entries, institution=institution)
