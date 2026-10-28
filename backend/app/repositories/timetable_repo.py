from typing import Optional, List, Tuple, Dict, Any
from datetime import time
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, distinct, func
from app.models.timetable import Timetable
from app.models.school_class import SchoolClass
from app.models.teacher import Teacher
from app.models.subject import Subject
from app.repositories.base_repo import BaseRepository
from app.schemas.timetable import TimetableConflictDetail, TimetableSummary, TimetableFilterOptions


class TimetableRepository(BaseRepository[Timetable]):
    """Repository for Timetable schedule entries, multi-conflict detection, and analytics."""

    def __init__(self, db: Session):
        super().__init__(Timetable, db)

    def collect_conflicts(
        self,
        class_id: int,
        day_of_week: str,
        start_time: time,
        end_time: time,
        academic_year: str,
        teacher_id: Optional[int] = None,
        room: Optional[str] = None,
        exclude_id: Optional[int] = None
    ) -> List[TimetableConflictDetail]:
        """
        Check for any overlapping schedule conflicts across:
        1. Class (Class cannot have two subjects at the same time)
        2. Teacher (Teacher cannot teach two classes at the same time)
        3. Room (Room cannot be occupied by two classes at the same time)
        """
        conflicts: List[TimetableConflictDetail] = []
        year_clean = academic_year.strip()
        year_variants = [year_clean, year_clean.replace("/", "-"), year_clean.replace("-", "/")]

        base_time_filter = and_(
            Timetable.day_of_week == day_of_week.strip(),
            Timetable.academic_year.in_(year_variants),
            Timetable.status.in_(["ACTIVE", "PUBLISHED", "DRAFT"]),
            Timetable.start_time < end_time,
            Timetable.end_time > start_time
        )

        # 1. Class Conflict
        class_query = self.db.query(Timetable).filter(
            base_time_filter,
            Timetable.class_id == class_id
        )
        if exclude_id:
            class_query = class_query.filter(Timetable.id != exclude_id)
        
        c_entry = class_query.first()
        if c_entry:
            class_name = c_entry.school_class.name if c_entry.school_class else f"Class {class_id}"
            subj_name = c_entry.subject.name if c_entry.subject else "Scheduled Subject"
            teacher_name = c_entry.teacher.full_name if c_entry.teacher else None
            conflicts.append(TimetableConflictDetail(
                conflict_type="CLASS",
                message=f"Class '{class_name}' already has '{subj_name}' scheduled on {day_of_week} ({c_entry.start_time.strftime('%H:%M')}–{c_entry.end_time.strftime('%H:%M')}).",
                conflicting_slot_id=c_entry.id,
                day_of_week=c_entry.day_of_week,
                start_time=c_entry.start_time.strftime('%H:%M'),
                end_time=c_entry.end_time.strftime('%H:%M'),
                class_name=class_name,
                teacher_name=teacher_name,
                room=c_entry.room,
                subject_name=subj_name
            ))

        # 2. Teacher Conflict
        if teacher_id:
            teacher_query = self.db.query(Timetable).filter(
                base_time_filter,
                Timetable.teacher_id == teacher_id
            )
            if exclude_id:
                teacher_query = teacher_query.filter(Timetable.id != exclude_id)
            
            t_entry = teacher_query.first()
            if t_entry:
                class_name = t_entry.school_class.name if t_entry.school_class else f"Class {t_entry.class_id}"
                subj_name = t_entry.subject.name if t_entry.subject else "Subject"
                teacher_name = t_entry.teacher.full_name if t_entry.teacher else f"Teacher {teacher_id}"
                conflicts.append(TimetableConflictDetail(
                    conflict_type="TEACHER",
                    message=f"Teacher '{teacher_name}' is already teaching '{subj_name}' for '{class_name}' on {day_of_week} ({t_entry.start_time.strftime('%H:%M')}–{t_entry.end_time.strftime('%H:%M')}).",
                    conflicting_slot_id=t_entry.id,
                    day_of_week=t_entry.day_of_week,
                    start_time=t_entry.start_time.strftime('%H:%M'),
                    end_time=t_entry.end_time.strftime('%H:%M'),
                    class_name=class_name,
                    teacher_name=teacher_name,
                    room=t_entry.room,
                    subject_name=subj_name
                ))

        # 3. Room Conflict
        if room and room.strip():
            room_clean = room.strip()
            room_query = self.db.query(Timetable).filter(
                base_time_filter,
                func.lower(Timetable.room) == room_clean.lower()
            )
            if exclude_id:
                room_query = room_query.filter(Timetable.id != exclude_id)
            
            r_entry = room_query.first()
            if r_entry:
                class_name = r_entry.school_class.name if r_entry.school_class else f"Class {r_entry.class_id}"
                subj_name = r_entry.subject.name if r_entry.subject else "Subject"
                teacher_name = r_entry.teacher.full_name if r_entry.teacher else None
                conflicts.append(TimetableConflictDetail(
                    conflict_type="ROOM",
                    message=f"Room '{r_entry.room}' is already booked for '{class_name}' on {day_of_week} ({r_entry.start_time.strftime('%H:%M')}–{r_entry.end_time.strftime('%H:%M')}).",
                    conflicting_slot_id=r_entry.id,
                    day_of_week=r_entry.day_of_week,
                    start_time=r_entry.start_time.strftime('%H:%M'),
                    end_time=r_entry.end_time.strftime('%H:%M'),
                    class_name=class_name,
                    teacher_name=teacher_name,
                    room=r_entry.room,
                    subject_name=subj_name
                ))

        return conflicts

    def detect_all_conflicts(self, academic_year: Optional[str] = None) -> List[TimetableConflictDetail]:
        """Scan active and published timetable entries for the academic year and find any mutual overlaps."""
        q = self.db.query(Timetable).filter(Timetable.status.in_(["ACTIVE", "PUBLISHED", "DRAFT"]))
        if academic_year and academic_year.strip():
            y = academic_year.strip()
            y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]
            q = q.filter(Timetable.academic_year.in_(y_variants))
        
        slots = q.all()
        detected: List[TimetableConflictDetail] = []
        seen_pairs = set()

        for i, s1 in enumerate(slots):
            for s2 in slots[i+1:]:
                # Check same day and same year (normalized)
                same_year = (s1.academic_year == s2.academic_year or
                             s1.academic_year.replace("/", "-") == s2.academic_year.replace("/", "-"))
                if s1.day_of_week.lower() != s2.day_of_week.lower() or not same_year:
                    continue
                # Overlap condition: start1 < end2 and end1 > start2
                if s1.start_time < s2.end_time and s1.end_time > s2.start_time:
                    pair_key = (min(s1.id, s2.id), max(s1.id, s2.id))
                    if pair_key in seen_pairs:
                        continue

                    # 1. Class conflict
                    if s1.class_id == s2.class_id:
                        seen_pairs.add(pair_key)
                        c_name = s1.school_class.name if s1.school_class else f"Class {s1.class_id}"
                        detected.append(TimetableConflictDetail(
                            conflict_type="CLASS",
                            message=f"Class '{c_name}' has overlapping slots: '{s1.subject.name if s1.subject else ''}' ({s1.start_time.strftime('%H:%M')}–{s1.end_time.strftime('%H:%M')}) and '{s2.subject.name if s2.subject else ''}' ({s2.start_time.strftime('%H:%M')}–{s2.end_time.strftime('%H:%M')}) on {s1.day_of_week}.",
                            conflicting_slot_id=s2.id,
                            day_of_week=s1.day_of_week,
                            start_time=s1.start_time.strftime('%H:%M'),
                            end_time=s1.end_time.strftime('%H:%M'),
                            class_name=c_name,
                            teacher_name=s1.teacher.full_name if s1.teacher else None,
                            room=s1.room,
                            subject_name=s1.subject.name if s1.subject else None
                        ))

                    # 2. Teacher conflict
                    elif s1.teacher_id and s2.teacher_id and s1.teacher_id == s2.teacher_id:
                        seen_pairs.add(pair_key)
                        t_name = s1.teacher.full_name if s1.teacher else f"Teacher {s1.teacher_id}"
                        c1_name = s1.school_class.name if s1.school_class else f"Class {s1.class_id}"
                        c2_name = s2.school_class.name if s2.school_class else f"Class {s2.class_id}"
                        detected.append(TimetableConflictDetail(
                            conflict_type="TEACHER",
                            message=f"Teacher '{t_name}' is scheduled for both '{c1_name}' ({s1.start_time.strftime('%H:%M')}–{s1.end_time.strftime('%H:%M')}) and '{c2_name}' ({s2.start_time.strftime('%H:%M')}–{s2.end_time.strftime('%H:%M')}) on {s1.day_of_week}.",
                            conflicting_slot_id=s2.id,
                            day_of_week=s1.day_of_week,
                            start_time=s1.start_time.strftime('%H:%M'),
                            end_time=s1.end_time.strftime('%H:%M'),
                            class_name=c1_name,
                            teacher_name=t_name,
                            room=s1.room,
                            subject_name=s1.subject.name if s1.subject else None
                        ))

                    # 3. Room conflict
                    elif s1.room and s2.room and s1.room.strip().lower() == s2.room.strip().lower():
                        seen_pairs.add(pair_key)
                        c1_name = s1.school_class.name if s1.school_class else f"Class {s1.class_id}"
                        c2_name = s2.school_class.name if s2.school_class else f"Class {s2.class_id}"
                        detected.append(TimetableConflictDetail(
                            conflict_type="ROOM",
                            message=f"Room '{s1.room}' is booked for both '{c1_name}' and '{c2_name}' on {s1.day_of_week} between {max(s1.start_time, s2.start_time).strftime('%H:%M')} and {min(s1.end_time, s2.end_time).strftime('%H:%M')}.",
                            conflicting_slot_id=s2.id,
                            day_of_week=s1.day_of_week,
                            start_time=s1.start_time.strftime('%H:%M'),
                            end_time=s1.end_time.strftime('%H:%M'),
                            class_name=c1_name,
                            teacher_name=s1.teacher.full_name if s1.teacher else None,
                            room=s1.room,
                            subject_name=s1.subject.name if s1.subject else None
                        ))

        return detected

    def get_summary(self, academic_year: Optional[str] = None) -> TimetableSummary:
        """Calculate real-time timetable summary metrics from PostgreSQL."""
        base_filter = [Timetable.status.in_(["ACTIVE", "PUBLISHED"])]
        if academic_year and academic_year.strip():
            y = academic_year.strip()
            y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]
            base_filter.append(Timetable.academic_year.in_(y_variants))

        total_periods = self.db.query(func.count(Timetable.id)).filter(*base_filter).scalar() or 0
        scheduled_classes = self.db.query(func.count(distinct(Timetable.class_id))).filter(*base_filter).scalar() or 0
        assigned_teachers = self.db.query(func.count(distinct(Timetable.teacher_id))).filter(
            *base_filter,
            Timetable.teacher_id.isnot(None)
        ).scalar() or 0
        active_rooms = self.db.query(func.count(distinct(Timetable.room))).filter(
            *base_filter,
            Timetable.room.isnot(None),
            Timetable.room != ""
        ).scalar() or 0

        conflicts = self.detect_all_conflicts(academic_year)

        return TimetableSummary(
            total_periods=total_periods,
            scheduled_classes=scheduled_classes,
            assigned_teachers=assigned_teachers,
            active_rooms=active_rooms,
            conflicts_count=len(conflicts),
            conflicts=conflicts
        )

    def get_filter_options(self, academic_year: Optional[str] = None) -> TimetableFilterOptions:
        """Get distinct filter options from PostgreSQL."""
        # 1. Distinct academic years from timetables and classes
        t_years = [y[0] for y in self.db.query(distinct(Timetable.academic_year)).all() if y[0]]
        c_years = [y[0] for y in self.db.query(distinct(SchoolClass.academic_year)).all() if y[0]]
        raw_years = t_years + c_years + ["2026/2027", "2025/2026"]
        
        # Deduplicate while preserving format
        seen_norm = set()
        clean_years = []
        for yr in sorted(raw_years, reverse=True):
            norm = yr.replace("-", "/")
            if norm not in seen_norm:
                seen_norm.add(norm)
                clean_years.append(yr)

        # 2. Days of week standard list
        days_of_week = [
            "Saturday",
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday"
        ]

        # 3. Distinct rooms
        q_rooms = self.db.query(distinct(Timetable.room)).filter(
            Timetable.room.isnot(None),
            Timetable.room != ""
        )
        if academic_year and academic_year.strip():
            y = academic_year.strip()
            y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]
            q_rooms = q_rooms.filter(Timetable.academic_year.in_(y_variants))
        rooms = [r[0] for r in q_rooms.all() if r[0]]
        if not rooms:
            rooms = ["Room 101", "Room 102", "Room 201", "Room 204", "Science Lab", "Computer Lab"]

        return TimetableFilterOptions(
            academic_years=clean_years,
            days_of_week=days_of_week,
            rooms=sorted(list(set(rooms)))
        )

    def search_timetable(
        self,
        class_id: Optional[int] = None,
        teacher_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        day_of_week: Optional[str] = None,
        academic_year: Optional[str] = None,
        room: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 200
    ) -> Tuple[List[Timetable], int]:
        q = self.db.query(Timetable)
        
        if status and status.strip() and status.strip().upper() != "ALL":
            q = q.filter(Timetable.status == status.strip().upper())
        else:
            q = q.filter(Timetable.status.in_(["ACTIVE", "PUBLISHED", "DRAFT"]))

        if class_id:
            q = q.filter(Timetable.class_id == class_id)
        if teacher_id:
            q = q.filter(Timetable.teacher_id == teacher_id)
        if subject_id:
            q = q.filter(Timetable.subject_id == subject_id)
        if day_of_week and day_of_week.strip() and day_of_week.upper() != "ALL":
            q = q.filter(func.lower(Timetable.day_of_week) == day_of_week.strip().lower())
        if academic_year and academic_year.strip():
            y = academic_year.strip()
            y_variants = [y, y.replace("/", "-"), y.replace("-", "/")]
            q = q.filter(Timetable.academic_year.in_(y_variants))
        if room and room.strip() and room.upper() != "ALL":
            q = q.filter(func.lower(Timetable.room) == room.strip().lower())

        total = q.count()
        # Order by Day, then start_time
        entries = q.order_by(
            Timetable.day_of_week.asc(),
            Timetable.start_time.asc(),
            Timetable.class_id.asc()
        ).offset(skip).limit(limit).all()

        return entries, total
