from datetime import date, datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from fastapi import HTTPException, status

from app.models.user import User
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.attendance import Attendance
from app.models.audit_log import AuditLog
from app.repositories.teacher_repo import TeacherRepository
from app.schemas.attendance import (
    TeacherAttendanceOptionsResponse,
    TeacherAttendanceClassOption,
    TeacherAttendanceSubjectOption,
    TeacherAttendanceRosterResponse,
    StudentAttendanceRosterItem,
    TeacherSaveAttendancePayload,
    TeacherAttendanceSessionItem,
    TeacherAttendanceSummaryResponse,
    TeacherStudentAttendanceSummaryItem,
    AbsentRecordDetail,
)


class TeacherAttendanceService:
    """Service strictly enforcing teacher assignment authorization for attendance management."""

    def __init__(self, db: Session):
        self.db = db
        self.teacher_repo = TeacherRepository(db)

    def get_authenticated_teacher(self, user: User) -> Teacher:
        teacher = self.teacher_repo.get_by_user_id(user.id)
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No faculty/teacher profile associated with this user account."
            )
        return teacher

    def verify_teacher_assignment(
        self,
        teacher_id: int,
        class_id: int,
        subject_id: int,
        academic_year: Optional[str] = None
    ) -> TeacherAssignment:
        query = self.db.query(TeacherAssignment).filter(
            TeacherAssignment.teacher_id == teacher_id,
            TeacherAssignment.class_id == class_id,
            TeacherAssignment.subject_id == subject_id,
            TeacherAssignment.status == "ACTIVE"
        )
        if academic_year:
            years = [academic_year, academic_year.replace("/", "-"), academic_year.replace("-", "/")]
            query = query.filter(TeacherAssignment.academic_year.in_(years))
        
        assignment = query.first()
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to manage attendance for this class and subject. Teacher assignment required."
            )
        return assignment

    def get_filter_options(self, user: User) -> TeacherAttendanceOptionsResponse:
        teacher = self.get_authenticated_teacher(user)
        assignments = self.teacher_repo.get_teacher_assignments(teacher.id)

        academic_years = sorted(list(set(a.academic_year for a in assignments)), reverse=True)
        
        classes_map = {}
        subjects_list = []

        for a in assignments:
            if a.class_id not in classes_map:
                classes_map[a.class_id] = TeacherAttendanceClassOption(
                    id=a.class_id,
                    name=a.school_class.name,
                    code=a.school_class.code,
                    academic_year=a.academic_year
                )
            subjects_list.append(
                TeacherAttendanceSubjectOption(
                    id=a.subject_id,
                    name=a.subject.name,
                    code=a.subject.code,
                    class_id=a.class_id
                )
            )

        # Deduplicate subjects per class
        unique_subjects = []
        seen_keys = set()
        for s in subjects_list:
            key = (s.id, s.class_id)
            if key not in seen_keys:
                seen_keys.add(key)
                unique_subjects.append(s)

        return TeacherAttendanceOptionsResponse(
            academic_years=academic_years if academic_years else ["2025-2026"],
            classes=list(classes_map.values()),
            subjects=unique_subjects
        )

    def get_attendance_roster(
        self,
        user: User,
        class_id: int,
        subject_id: int,
        attendance_date: date,
        academic_year: Optional[str] = None,
        period: Optional[str] = None
    ) -> TeacherAttendanceRosterResponse:
        teacher = self.get_authenticated_teacher(user)
        assignment = self.verify_teacher_assignment(teacher.id, class_id, subject_id, academic_year)

        # Validate date: Disallow future dates
        today = date.today()
        if attendance_date > today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Attendance date cannot be in the future (Today is {today.isoformat()})."
            )

        # Query enrolled active students scoped to academic year
        target_year = academic_year or assignment.academic_year or assignment.school_class.academic_year
        enr_query = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == class_id,
            StudentEnrollment.status == "ACTIVE"
        )
        if target_year:
            years = [target_year, target_year.replace("/", "-"), target_year.replace("-", "/")]
            enr_query = enr_query.filter(StudentEnrollment.academic_year.in_(years))
        
        enrollments = enr_query.join(Student).order_by(Student.first_name.asc(), Student.last_name.asc()).all()

        # Graceful fallback: If no enrollments found for the specific year string, fetch all active students enrolled in this class
        if not enrollments:
            enrollments = self.db.query(StudentEnrollment).filter(
                StudentEnrollment.class_id == class_id,
                StudentEnrollment.status == "ACTIVE"
            ).join(Student).order_by(Student.first_name.asc(), Student.last_name.asc()).all()

        # Query existing attendance records
        att_records = self.db.query(Attendance).filter(
            Attendance.class_id == class_id,
            Attendance.subject_id == subject_id,
            Attendance.date == attendance_date
        )
        if period is not None:
            att_records = att_records.filter(Attendance.period == period)
        else:
            att_records = att_records.filter(Attendance.period.is_(None))
        
        att_list = att_records.all()
        att_map: Dict[int, Attendance] = {a.student_id: a for a in att_list}

        is_recorded = len(att_list) > 0
        roster_items: List[StudentAttendanceRosterItem] = []
        present_count = 0
        absent_count = 0
        seen_student_ids = set()

        for enr in enrollments:
            std = enr.student
            if not std or std.status != "ACTIVE" or std.id in seen_student_ids:
                continue
            seen_student_ids.add(std.id)

            if std.id in att_map:
                existing = att_map[std.id]
                status_val = existing.status
                remarks_val = existing.remarks
                att_id = existing.id
            else:
                # Default for new attendance: ALL STUDENTS DEFAULT TO PRESENT / ON
                status_val = "PRESENT"
                remarks_val = None
                att_id = None

            if status_val in ["PRESENT", "LATE"]:
                present_count += 1
            else:
                absent_count += 1

            roster_items.append(
                StudentAttendanceRosterItem(
                    student_id=std.id,
                    student_name=std.full_name,
                    admission_number=std.admission_number,
                    gender=std.gender,
                    status=status_val,
                    remarks=remarks_val,
                    attendance_id=att_id
                )
            )

        return TeacherAttendanceRosterResponse(
            class_id=class_id,
            class_name=assignment.school_class.name,
            subject_id=subject_id,
            subject_name=assignment.subject.name,
            date=attendance_date,
            period=period,
            academic_year=target_year,
            is_recorded=is_recorded,
            total_students=len(roster_items),
            present_count=present_count,
            absent_count=absent_count,
            students=roster_items
        )

    def save_attendance(
        self,
        user: User,
        payload: TeacherSaveAttendancePayload
    ) -> Dict[str, Any]:
        teacher = self.get_authenticated_teacher(user)
        assignment = self.verify_teacher_assignment(
            teacher.id,
            payload.class_id,
            payload.subject_id,
            payload.academic_year
        )

        today = date.today()
        if payload.date > today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Attendance cannot be recorded for future dates (Today is {today.isoformat()})."
            )

        if not payload.entries:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Attendance entries cannot be empty."
            )

        # Get valid enrolled student IDs in this class for academic year
        target_year = payload.academic_year or assignment.academic_year or assignment.school_class.academic_year
        enr_query = self.db.query(StudentEnrollment.student_id).filter(
            StudentEnrollment.class_id == payload.class_id,
            StudentEnrollment.status == "ACTIVE"
        )
        if target_year:
            years = [target_year, target_year.replace("/", "-"), target_year.replace("-", "/")]
            enr_query = enr_query.filter(StudentEnrollment.academic_year.in_(years))
        enrolled_ids = set(s[0] for s in enr_query.all())
        if not enrolled_ids:
            enrolled_ids = set(
                s[0] for s in self.db.query(StudentEnrollment.student_id).filter(
                    StudentEnrollment.class_id == payload.class_id,
                    StudentEnrollment.status == "ACTIVE"
                ).all()
            )

        present_count = 0
        absent_count = 0
        saved_count = 0

        # Deduplicate payload entries by student_id to prevent duplicates
        unique_entries = {e.student_id: e for e in payload.entries}

        # Run within transaction
        for entry in unique_entries.values():
            if entry.student_id not in enrolled_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Student ID {entry.student_id} is not enrolled in class {assignment.school_class.name}."
                )

            valid_status = entry.status.upper() if entry.status else "PRESENT"
            if valid_status not in ["PRESENT", "ABSENT", "EXCUSED", "LATE"]:
                valid_status = "PRESENT"

            if valid_status in ["PRESENT", "LATE"]:
                present_count += 1
            else:
                absent_count += 1

            # Check if record exists
            existing_query = self.db.query(Attendance).filter(
                Attendance.student_id == entry.student_id,
                Attendance.class_id == payload.class_id,
                Attendance.subject_id == payload.subject_id,
                Attendance.date == payload.date
            )
            if payload.period is not None:
                existing_query = existing_query.filter(Attendance.period == payload.period)
            else:
                existing_query = existing_query.filter(Attendance.period.is_(None))
            existing = existing_query.first()

            if existing:
                existing.status = valid_status
                existing.remarks = entry.remarks.strip() if entry.remarks else None
                existing.recorded_by_id = user.id
                existing.teacher_id = teacher.id
                existing.academic_year = payload.academic_year
            else:
                new_record = Attendance(
                    student_id=entry.student_id,
                    class_id=payload.class_id,
                    subject_id=payload.subject_id,
                    teacher_id=teacher.id,
                    academic_year=payload.academic_year,
                    date=payload.date,
                    period=payload.period,
                    status=valid_status,
                    remarks=entry.remarks.strip() if entry.remarks else None,
                    recorded_by_id=user.id
                )
                self.db.add(new_record)

            saved_count += 1

        # Audit log entry
        audit = AuditLog(
            user_id=user.id,
            action="SAVE_ATTENDANCE",
            status="SUCCESS",
            details={
                "class_id": payload.class_id,
                "class_name": assignment.school_class.name,
                "subject_id": payload.subject_id,
                "subject_name": assignment.subject.name,
                "date": payload.date.isoformat(),
                "present_count": present_count,
                "absent_count": absent_count
            }
        )
        self.db.add(audit)
        self.db.commit()

        # Trigger automatic guardian absence notification (idempotent, checks system settings)
        if absent_count > 0:
            try:
                from app.services.notification_service import NotificationService
                notif_service = NotificationService(self.db)
                notif_service.trigger_attendance_absence_notifications(
                    class_id=payload.class_id,
                    subject_id=payload.subject_id,
                    attendance_date=payload.date,
                    period=payload.period,
                    recorded_by_id=user.id,
                )
            except Exception:
                pass

        return {
            "message": "Attendance successfully saved and persisted to PostgreSQL.",
            "class_id": payload.class_id,
            "class_name": assignment.school_class.name,
            "subject_id": payload.subject_id,
            "subject_name": assignment.subject.name,
            "date": payload.date.isoformat(),
            "period": payload.period,
            "total_saved": saved_count,
            "present_count": present_count,
            "absent_count": absent_count,
        }


    def get_attendance_history(
        self,
        user: User,
        class_id: Optional[int] = None,
        academic_year: Optional[str] = None
    ) -> List[TeacherAttendanceSessionItem]:
        teacher = self.get_authenticated_teacher(user)
        assignments = self.teacher_repo.get_teacher_assignments(teacher.id)

        assigned_class_ids = list(set(a.class_id for a in assignments))
        assigned_subject_ids = list(set(a.subject_id for a in assignments))

        if not assigned_class_ids or not assigned_subject_ids:
            return []

        query = self.db.query(
            Attendance.date,
            Attendance.period,
            Attendance.class_id,
            Attendance.subject_id,
            Attendance.academic_year,
            func.count(Attendance.id).label("total_students"),
            func.sum(case_present()).label("present_count"),
            func.sum(case_absent()).label("absent_count"),
            func.max(Attendance.created_at).label("recorded_at")
        ).filter(
            Attendance.class_id.in_(assigned_class_ids),
            Attendance.subject_id.in_(assigned_subject_ids)
        )

        if class_id:
            if class_id not in assigned_class_ids:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to unassigned class denied.")
            query = query.filter(Attendance.class_id == class_id)

        if academic_year:
            query = query.filter(Attendance.academic_year == academic_year)

        rows = query.group_by(
            Attendance.date,
            Attendance.period,
            Attendance.class_id,
            Attendance.subject_id,
            Attendance.academic_year
        ).order_by(Attendance.date.desc()).limit(100).all()

        classes_map = {c.id: c.name for c in self.db.query(SchoolClass).filter(SchoolClass.id.in_(assigned_class_ids)).all()}
        subjects_map = {s.id: s.name for s in self.db.query(Subject).filter(Subject.id.in_(assigned_subject_ids)).all()}

        sessions: List[TeacherAttendanceSessionItem] = []
        for r in rows:
            tot = r.total_students or 0
            pres = int(r.present_count or 0)
            abs_c = int(r.absent_count or 0)
            pct = round((pres / tot * 100), 1) if tot > 0 else 0.0

            s_key = f"{r.class_id}_{r.subject_id}_{r.date}_{r.period or 'daily'}"
            sessions.append(
                TeacherAttendanceSessionItem(
                    session_key=s_key,
                    date=r.date,
                    period=r.period,
                    class_id=r.class_id,
                    class_name=classes_map.get(r.class_id, f"Class {r.class_id}"),
                    subject_id=r.subject_id,
                    subject_name=subjects_map.get(r.subject_id, f"Subject {r.subject_id}"),
                    academic_year=r.academic_year,
                    total_students=tot,
                    present_count=pres,
                    absent_count=abs_c,
                    attendance_percentage=pct,
                    recorded_at=r.recorded_at
                )
            )

        return sessions

    def get_class_student_summary(
        self,
        user: User,
        class_id: int,
        subject_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> TeacherAttendanceSummaryResponse:
        teacher = self.get_authenticated_teacher(user)
        assignments = self.teacher_repo.get_teacher_assignments(teacher.id)

        assigned_for_class = [a for a in assignments if a.class_id == class_id]
        if not assigned_for_class:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view attendance statistics for this class."
            )

        target_subject = None
        if subject_id:
            match = next((a for a in assigned_for_class if a.subject_id == subject_id), None)
            if not match:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized for this subject."
                )
            target_subject = match.subject

        school_class = assigned_for_class[0].school_class

        # Enrolled students
        enrollments = self.db.query(StudentEnrollment).filter(
            StudentEnrollment.class_id == class_id,
            StudentEnrollment.status == "ACTIVE"
        ).join(Student).order_by(Student.first_name.asc()).all()

        student_summaries: List[TeacherStudentAttendanceSummaryItem] = []
        overall_sessions_set = set()

        for enr in enrollments:
            std = enr.student
            if not std:
                continue

            att_query = self.db.query(Attendance).filter(
                Attendance.student_id == std.id,
                Attendance.class_id == class_id
            )
            if subject_id:
                att_query = att_query.filter(Attendance.subject_id == subject_id)
            else:
                allowed_subjects = [a.subject_id for a in assigned_for_class]
                att_query = att_query.filter(Attendance.subject_id.in_(allowed_subjects))

            if start_date:
                att_query = att_query.filter(Attendance.date >= start_date)
            if end_date:
                att_query = att_query.filter(Attendance.date <= end_date)

            records = att_query.order_by(Attendance.date.desc()).all()

            tot = len(records)
            pres = sum(1 for r in records if r.status in ["PRESENT", "LATE"])
            absc = sum(1 for r in records if r.status == "ABSENT")
            exc = sum(1 for r in records if r.status == "EXCUSED")
            pct = round((pres / tot * 100), 1) if tot > 0 else 100.0

            abs_hist: List[AbsentRecordDetail] = []
            for r in records:
                overall_sessions_set.add((r.date, r.subject_id, r.period))
                if r.status in ["ABSENT", "EXCUSED"]:
                    abs_hist.append(
                        AbsentRecordDetail(
                            date=r.date,
                            period=r.period,
                            subject_name=r.subject.name if r.subject else "",
                            status=r.status,
                            remarks=r.remarks
                        )
                    )

            student_summaries.append(
                TeacherStudentAttendanceSummaryItem(
                    student_id=std.id,
                    student_name=std.full_name,
                    admission_number=std.admission_number,
                    class_id=class_id,
                    class_name=school_class.name,
                    total_sessions=tot,
                    present_count=pres,
                    absent_count=absc,
                    excused_count=exc,
                    attendance_percentage=pct,
                    absent_history=abs_hist
                )
            )

        return TeacherAttendanceSummaryResponse(
            class_id=class_id,
            class_name=school_class.name,
            subject_id=target_subject.id if target_subject else None,
            subject_name=target_subject.name if target_subject else None,
            total_sessions=len(overall_sessions_set),
            students=student_summaries
        )


def case_present():
    from sqlalchemy import case
    return case((Attendance.status.in_(["PRESENT", "LATE"]), 1), else_=0)


def case_absent():
    from sqlalchemy import case
    return case((Attendance.status == "ABSENT", 1), else_=0)
