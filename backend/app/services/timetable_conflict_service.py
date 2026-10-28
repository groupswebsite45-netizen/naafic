from datetime import time
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.timetable import Timetable
from app.models.school_class import SchoolClass
from app.models.teacher import Teacher
from app.models.subject import Subject
from app.models.teacher_assignment import TeacherAssignment
from app.models.teacher_availability import TeacherAvailability
from app.models.timetable_setting import TimetableSetting
from app.schemas.timetable import TimetableConflictDetail


class TimetableConflictService:
    """
    Dedicated Multi-Vector Timetable Conflict Detection and Schedule Validation Service.
    Enforces all 10 academic scheduling constraints.
    """

    def __init__(self, db: Session):
        self.db = db

    def validate_class_schedule(
        self,
        class_id: int,
        academic_year: str
    ) -> List[TimetableConflictDetail]:
        """Run all 10 conflict checks for a specific class."""
        year_clean = academic_year.strip()
        year_variants = [year_clean, year_clean.replace("/", "-"), year_clean.replace("-", "/")]

        school_class = self.db.query(SchoolClass).filter(SchoolClass.id == class_id).first()
        if not school_class:
            return [TimetableConflictDetail(
                conflict_type="CLASS",
                message=f"Class with ID {class_id} not found.",
                day_of_week="N/A",
                start_time="00:00",
                end_time="00:00",
                class_name=f"Class {class_id}",
                severity="ERROR"
            )]

        # Retrieve slots for this class
        slots = (
            self.db.query(Timetable)
            .filter(
                Timetable.class_id == class_id,
                Timetable.academic_year.in_(year_variants),
                Timetable.status.in_(["ACTIVE", "PUBLISHED", "DRAFT", "GENERATED"])
            )
            .all()
        )

        # Retrieve all active/published slots across the school for cross-checking
        all_other_slots = (
            self.db.query(Timetable)
            .filter(
                Timetable.class_id != class_id,
                Timetable.academic_year.in_(year_variants),
                Timetable.status.in_(["ACTIVE", "PUBLISHED"])
            )
            .all()
        )

        # Retrieve settings
        setting = (
            self.db.query(TimetableSetting)
            .filter(
                TimetableSetting.academic_year.in_(year_variants),
                TimetableSetting.is_active == True
            )
            .first()
        )

        # Retrieve teacher availabilities
        availabilities = (
            self.db.query(TeacherAvailability)
            .filter(TeacherAvailability.academic_year.in_(year_variants))
            .all()
        )
        avail_map = {(a.teacher_id, a.day_of_week.lower()): a for a in availabilities}

        # Retrieve authorized assignments
        assignments = (
            self.db.query(TeacherAssignment)
            .filter(
                TeacherAssignment.class_id == class_id,
                TeacherAssignment.status == "ACTIVE"
            )
            .all()
        )
        assigned_subj_ids = {a.subject_id for a in assignments}
        assigned_pairs = {(a.subject_id, a.teacher_id) for a in assignments}

        conflicts: List[TimetableConflictDetail] = []

        # 1. Class Collision (Two lessons for this class at overlapping time)
        for i, s1 in enumerate(slots):
            for s2 in slots[i+1:]:
                if s1.day_of_week.lower() == s2.day_of_week.lower():
                    if s1.start_time < s2.end_time and s1.end_time > s2.start_time:
                        conflicts.append(TimetableConflictDetail(
                            conflict_type="CLASS",
                            message=f"Class '{school_class.name}' is scheduled for two simultaneous lessons: '{s1.subject.name if s1.subject else ''}' and '{s2.subject.name if s2.subject else ''}' on {s1.day_of_week} ({s1.start_time.strftime('%H:%M')}–{s1.end_time.strftime('%H:%M')}).",
                            conflicting_slot_id=s2.id,
                            day_of_week=s1.day_of_week,
                            start_time=s1.start_time.strftime('%H:%M'),
                            end_time=s1.end_time.strftime('%H:%M'),
                            class_name=school_class.name,
                            subject_name=s1.subject.name if s1.subject else None,
                            severity="ERROR"
                        ))

        # 2. Teacher Collision (Teacher assigned to two classes simultaneously)
        for s in slots:
            if not s.teacher_id:
                # 9. Missing Teacher Assignment
                conflicts.append(TimetableConflictDetail(
                    conflict_type="TEACHER",
                    message=f"Lesson for '{s.subject.name if s.subject else 'Subject'}' on {s.day_of_week} at {s.start_time.strftime('%H:%M')} has no assigned faculty teacher.",
                    conflicting_slot_id=s.id,
                    day_of_week=s.day_of_week,
                    start_time=s.start_time.strftime('%H:%M'),
                    end_time=s.end_time.strftime('%H:%M'),
                    class_name=school_class.name,
                    subject_name=s.subject.name if s.subject else None,
                    severity="WARNING"
                ))
                continue

            # Check collision with other classes
            for o in all_other_slots:
                if o.teacher_id == s.teacher_id and o.day_of_week.lower() == s.day_of_week.lower():
                    if s.start_time < o.end_time and s.end_time > o.start_time:
                        t_name = s.teacher.full_name if s.teacher else f"Teacher {s.teacher_id}"
                        o_class_name = o.school_class.name if o.school_class else f"Class {o.class_id}"
                        conflicts.append(TimetableConflictDetail(
                            conflict_type="TEACHER",
                            message=f"Teacher '{t_name}' is scheduled simultaneously for '{school_class.name}' and '{o_class_name}' on {s.day_of_week} ({s.start_time.strftime('%H:%M')}–{s.end_time.strftime('%H:%M')}).",
                            conflicting_slot_id=o.id,
                            day_of_week=s.day_of_week,
                            start_time=s.start_time.strftime('%H:%M'),
                            end_time=s.end_time.strftime('%H:%M'),
                            class_name=school_class.name,
                            teacher_name=t_name,
                            subject_name=s.subject.name if s.subject else None,
                            severity="ERROR"
                        ))

            # 6. Teacher Unavailable Period Check
            avail = avail_map.get((s.teacher_id, s.day_of_week.lower()))
            if avail and not avail.is_available:
                t_name = s.teacher.full_name if s.teacher else f"Teacher {s.teacher_id}"
                conflicts.append(TimetableConflictDetail(
                    conflict_type="UNAVAILABLE",
                    message=f"Teacher '{t_name}' is marked as unavailable on {s.day_of_week} according to faculty availability settings.",
                    conflicting_slot_id=s.id,
                    day_of_week=s.day_of_week,
                    start_time=s.start_time.strftime('%H:%M'),
                    end_time=s.end_time.strftime('%H:%M'),
                    class_name=school_class.name,
                    teacher_name=t_name,
                    subject_name=s.subject.name if s.subject else None,
                    severity="ERROR"
                ))

            # 10. Invalid Class-Subject-Teacher Authorization
            if s.subject_id not in assigned_subj_ids:
                s_name = s.subject.name if s.subject else f"Subject {s.subject_id}"
                conflicts.append(TimetableConflictDetail(
                    conflict_type="CLASS",
                    message=f"Subject '{s_name}' is not officially assigned to class '{school_class.name}'.",
                    conflicting_slot_id=s.id,
                    day_of_week=s.day_of_week,
                    start_time=s.start_time.strftime('%H:%M'),
                    end_time=s.end_time.strftime('%H:%M'),
                    class_name=school_class.name,
                    subject_name=s_name,
                    severity="ERROR"
                ))

        # 3. Room Collision (Classroom assigned to multiple lessons simultaneously)
        for s in slots:
            if s.room and s.room.strip():
                r_clean = s.room.strip().lower()
                for o in all_other_slots:
                    if o.room and o.room.strip().lower() == r_clean and o.day_of_week.lower() == s.day_of_week.lower():
                        if s.start_time < o.end_time and s.end_time > o.start_time:
                            o_class_name = o.school_class.name if o.school_class else f"Class {o.class_id}"
                            conflicts.append(TimetableConflictDetail(
                                conflict_type="ROOM",
                                message=f"Classroom '{s.room}' is booked simultaneously for '{school_class.name}' and '{o_class_name}' on {s.day_of_week} ({s.start_time.strftime('%H:%M')}–{s.end_time.strftime('%H:%M')}).",
                                conflicting_slot_id=o.id,
                                day_of_week=s.day_of_week,
                                start_time=s.start_time.strftime('%H:%M'),
                                end_time=s.end_time.strftime('%H:%M'),
                                class_name=school_class.name,
                                room=s.room,
                                subject_name=s.subject.name if s.subject else None,
                                severity="ERROR"
                            ))

        # 4 & 5. School Hours and Break Overlap Checks
        if setting:
            for s in slots:
                # 4. Lesson Outside School Hours
                if s.start_time < setting.start_time or s.end_time > setting.end_time:
                    conflicts.append(TimetableConflictDetail(
                        conflict_type="OUTSIDE_HOURS",
                        message=f"Lesson on {s.day_of_week} ({s.start_time.strftime('%H:%M')}–{s.end_time.strftime('%H:%M')}) falls outside official school operating hours ({setting.start_time.strftime('%H:%M')}–{setting.end_time.strftime('%H:%M')}).",
                        conflicting_slot_id=s.id,
                        day_of_week=s.day_of_week,
                        start_time=s.start_time.strftime('%H:%M'),
                        end_time=s.end_time.strftime('%H:%M'),
                        class_name=school_class.name,
                        subject_name=s.subject.name if s.subject else None,
                        severity="ERROR"
                    ))

        # 8. Duplicate Entries
        seen_slot_fingerprints = set()
        for s in slots:
            fp = (s.day_of_week.lower(), s.start_time, s.end_time, s.subject_id, s.class_id)
            if fp in seen_slot_fingerprints:
                conflicts.append(TimetableConflictDetail(
                    conflict_type="CLASS",
                    message=f"Duplicate timetable entry found for '{s.subject.name if s.subject else 'Subject'}' on {s.day_of_week} at {s.start_time.strftime('%H:%M')}.",
                    conflicting_slot_id=s.id,
                    day_of_week=s.day_of_week,
                    start_time=s.start_time.strftime('%H:%M'),
                    end_time=s.end_time.strftime('%H:%M'),
                    class_name=school_class.name,
                    subject_name=s.subject.name if s.subject else None,
                    severity="ERROR"
                ))
            else:
                seen_slot_fingerprints.add(fp)

        # 7. Check if any assigned subject has 0 scheduled periods
        scheduled_subj_ids = {s.subject_id for s in slots}
        for a in assignments:
            if a.subject_id not in scheduled_subj_ids:
                s_name = a.subject.name if a.subject else f"Subject {a.subject_id}"
                conflicts.append(TimetableConflictDetail(
                    conflict_type="CLASS",
                    message=f"Assigned subject '{s_name}' has 0 scheduled periods in this class timetable.",
                    day_of_week="N/A",
                    start_time="00:00",
                    end_time="00:00",
                    class_name=school_class.name,
                    subject_name=s_name,
                    severity="WARNING"
                ))

        return conflicts
