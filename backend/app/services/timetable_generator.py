from datetime import time, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from types import SimpleNamespace
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.utils.logger import logger

from app.models.timetable import Timetable
from app.models.school_class import SchoolClass
from app.models.teacher import Teacher
from app.models.subject import Subject
from app.models.teacher_assignment import TeacherAssignment
from app.models.teacher_availability import TeacherAvailability
from app.models.timetable_setting import TimetableSetting
from app.schemas.timetable import (
    TimetableGenerateRequest,
    TimetableGenerateResponse,
    TimetableConflictDetail,
    TimetableResponse,
    SubjectRequirement
)


class TimetableGenerator:
    """
    Intelligent Constraint-Satisfaction Automated Timetable Generation Engine.
    Respects school hours, period durations, breaks, teacher assignments,
    teacher availability, existing commitments, and curriculum workload distribution.
    """

    def __init__(self, db: Session):
        self.db = db

    def generate_for_class(
        self,
        request: TimetableGenerateRequest,
        user_id: Optional[int] = None
    ) -> TimetableGenerateResponse:
        school_class = self.db.query(SchoolClass).filter(SchoolClass.id == request.class_id).first()
        if not school_class:
            return TimetableGenerateResponse(
                success=False,
                class_id=request.class_id,
                class_name="Unknown",
                academic_year=request.academic_year,
                total_generated_periods=0,
                message=f"Class with ID {request.class_id} not found."
            )

        # 1. Resolve Academic Year Variants
        year_clean = request.academic_year.strip()
        year_variants = {year_clean, year_clean.replace("/", "-"), year_clean.replace("-", "/")}
        if school_class.academic_year:
            cy = school_class.academic_year.strip()
            year_variants.update([cy, cy.replace("/", "-"), cy.replace("-", "/")])
        year_variants_list = list(year_variants)

        # 2. Resolve Timetable Configuration Settings
        config = self._resolve_settings(request, school_class.division)

        # 3. Retrieve Authorized Subject & Teacher Assignments for this class
        assignments = (
            self.db.query(TeacherAssignment)
            .filter(
                TeacherAssignment.class_id == school_class.id,
                TeacherAssignment.status == "ACTIVE",
                TeacherAssignment.academic_year.in_(year_variants_list)
            )
            .all()
        )

        # Fallback if no exact year matches: query active assignments for class regardless of year variant
        if not assignments:
            assignments = (
                self.db.query(TeacherAssignment)
                .filter(
                    TeacherAssignment.class_id == school_class.id,
                    TeacherAssignment.status == "ACTIVE"
                )
                .all()
            )

        # Fallback to institutional curriculum subjects if no specific teacher assignments exist yet
        if not assignments:
            div = school_class.division or "ALL"
            curr_subjects = (
                self.db.query(Subject)
                .filter(
                    Subject.status == "ACTIVE",
                    Subject.division.in_([div, "ALL"])
                )
                .all()
            )
            if not curr_subjects:
                curr_subjects = self.db.query(Subject).filter(Subject.status == "ACTIVE").all()

            if not curr_subjects:
                return TimetableGenerateResponse(
                    success=False,
                    class_id=school_class.id,
                    class_name=school_class.name,
                    academic_year=request.academic_year,
                    total_generated_periods=0,
                    message="No active academic curriculum subjects found in the system. Please create subjects first."
                )

            from types import SimpleNamespace
            assignments = [
                SimpleNamespace(
                    id=0,
                    class_id=school_class.id,
                    subject_id=sub.id,
                    teacher_id=None,
                    academic_year=year_clean,
                    status="ACTIVE",
                    subject=sub,
                    teacher=None
                )
                for sub in curr_subjects
            ]

        # 4. Build Subject Requirements
        requirements = self._build_requirements(
            assignments,
            request.subject_requirements,
            request.subject_lessons_distribution
        )

        # 5. Generate Daily Period Slot Definitions
        # e.g., Period 1 (07:30-08:15), Period 2 (08:15-09:00), etc.
        period_slots = self._build_period_slots(config)

        if not period_slots:
            return TimetableGenerateResponse(
                success=False,
                class_id=school_class.id,
                class_name=school_class.name,
                academic_year=request.academic_year,
                total_generated_periods=0,
                message="Invalid timetable schedule configuration: No valid period slots could be calculated."
            )

        # 6. Retrieve Existing Timetable Commitments (Other classes and this class's preserved published slots)
        should_replace = request.replace_existing or getattr(request, "overwrite_existing", False)
        existing_other_slots = (
            self.db.query(Timetable)
            .filter(
                Timetable.class_id != school_class.id,
                Timetable.status.in_(["ACTIVE", "PUBLISHED"]),
                Timetable.academic_year.in_(year_variants_list)
            )
            .all()
        )
        if not should_replace or not getattr(request, "replace_published", False):
            class_published = (
                self.db.query(Timetable)
                .filter(
                    Timetable.class_id == school_class.id,
                    Timetable.status == "PUBLISHED",
                    Timetable.academic_year.in_(year_variants_list)
                )
                .all()
            )
            existing_other_slots.extend(class_published)

        # 7. Retrieve Teacher Availability records
        availabilities = (
            self.db.query(TeacherAvailability)
            .filter(
                TeacherAvailability.academic_year.in_(year_variants_list)
            )
            .all()
        )
        teacher_avail_map: Dict[Tuple[int, str], TeacherAvailability] = {
            (a.teacher_id, a.day_of_week.lower()): a for a in availabilities
        }

        # 8. Execute Constraint-Satisfaction Scheduling Algorithm
        VALID_DAYS = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        VALID_DAYS_MAP = {d.lower(): d for d in VALID_DAYS}
        raw_days = [d.strip() for d in config.school_days.split(",") if d.strip()]
        days = [VALID_DAYS_MAP[d.lower()] for d in raw_days if d.lower() in VALID_DAYS_MAP]
        if not days:
            days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
        default_room = request.default_room or f"Room {school_class.code or school_class.name}"

        scheduled_slots, conflicts, unassigned = self._schedule_csp(
            school_class=school_class,
            academic_year=year_clean,
            days=days,
            period_slots=period_slots,
            requirements=requirements,
            existing_other_slots=existing_other_slots,
            teacher_avail_map=teacher_avail_map,
            default_room=default_room
        )

        # 9. If replace_existing or overwrite_existing, clean up old non-published slots for this class
        if should_replace and scheduled_slots:
            delete_q = self.db.query(Timetable).filter(
                Timetable.class_id == school_class.id,
                Timetable.academic_year.in_(year_variants_list)
            )
            if not getattr(request, "replace_published", False):
                delete_q = delete_q.filter(Timetable.status != "PUBLISHED")
            delete_q.delete(synchronize_session=False)
            self.db.flush()

        # 10. Persist Generated Slots
        persisted_entries: List[Timetable] = []
        for slot in scheduled_slots:
            new_entry = Timetable(
                class_id=school_class.id,
                subject_id=slot["subject_id"],
                teacher_id=slot["teacher_id"],
                academic_year=year_clean,
                day_of_week=slot["day_of_week"],
                start_time=slot["start_time"],
                end_time=slot["end_time"],
                room=slot["room"],
                period_number=slot["period_number"],
                is_break=slot.get("is_break", False),
                status="GENERATED"
            )
            self.db.add(new_entry)
            persisted_entries.append(new_entry)

        self.db.commit()

        # Build response objects
        response_entries = []
        for e in persisted_entries:
            self.db.refresh(e)
            item = TimetableResponse(
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
                is_break=e.is_break,
                status=e.status,
                published_at=e.published_at,
                published_by_id=e.published_by_id,
                class_name=school_class.name,
                class_code=school_class.code,
                subject_name=e.subject.name if e.subject else None,
                subject_code=e.subject.code if e.subject else None,
                teacher_name=e.teacher.full_name if e.teacher else None,
                room_number=e.room,
                school_class=None,
                subject=None,
                teacher=None,
                created_at=e.created_at,
                updated_at=e.updated_at
            )
            response_entries.append(item)

        msg = f"Generated {len(response_entries)} weekly timetable periods across {len(days)} school days."
        if unassigned:
            msg += f" Note: {len(unassigned)} requirements could not be placed due to conflicts."

        return TimetableGenerateResponse(
            success=len(response_entries) > 0,
            class_id=school_class.id,
            class_name=school_class.name,
            academic_year=year_clean,
            total_generated_periods=len(response_entries),
            total_slots_generated=len(response_entries),
            generated_entries=response_entries,
            slots=response_entries,
            conflicts=conflicts,
            unassigned_requirements=unassigned,
            unplaced_subjects=unassigned,
            message=msg
        )

    def _resolve_settings(self, request: TimetableGenerateRequest, division: str) -> SimpleNamespace:
        """Resolve active TimetableSetting into an unattached configuration object without mutating database state."""
        year_clean = request.academic_year.strip()
        year_variants = [year_clean, year_clean.replace("/", "-"), year_clean.replace("-", "/")]

        setting = (
            self.db.query(TimetableSetting)
            .filter(
                TimetableSetting.academic_year.in_(year_variants),
                TimetableSetting.is_active == True
            )
            .first()
        )

        config = SimpleNamespace(
            academic_year=setting.academic_year if setting else year_clean,
            division=setting.division if setting else (division or "ALL"),
            school_days=setting.school_days if setting else "Saturday,Sunday,Monday,Tuesday,Wednesday,Thursday",
            start_time=setting.start_time if setting else time(7, 30),
            end_time=setting.end_time if setting else time(13, 30),
            period_duration_minutes=setting.period_duration_minutes if setting else 45,
            break_duration_minutes=setting.break_duration_minutes if setting else 20,
            break_after_period=setting.break_after_period if setting else 3,
            lunch_duration_minutes=setting.lunch_duration_minutes if setting else 30,
            lunch_after_period=setting.lunch_after_period if setting else 5,
            periods_per_day=setting.periods_per_day if setting else 6,
            is_active=True
        )

        VALID_DAYS = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        VALID_DAYS_MAP = {d.lower(): d for d in VALID_DAYS}

        # Override from explicit request options if provided, strictly normalizing day names
        if request.school_days:
            if isinstance(request.school_days, list):
                resolved_days = []
                for d in request.school_days:
                    d_clean = str(d).strip().capitalize()
                    if d_clean.lower() in VALID_DAYS_MAP and VALID_DAYS_MAP[d_clean.lower()] not in resolved_days:
                        resolved_days.append(VALID_DAYS_MAP[d_clean.lower()])
                if resolved_days:
                    config.school_days = ",".join(resolved_days)
            elif isinstance(request.school_days, str):
                parts = [p.strip().capitalize() for p in request.school_days.split(",") if p.strip()]
                resolved_days = [VALID_DAYS_MAP[p.lower()] for p in parts if p.lower() in VALID_DAYS_MAP]
                if resolved_days:
                    config.school_days = ",".join(resolved_days)

        if request.start_time:
            if isinstance(request.start_time, str):
                p = request.start_time.split(":")
                config.start_time = time(int(p[0]), int(p[1]))
            else:
                config.start_time = request.start_time
        if request.end_time:
            if isinstance(request.end_time, str):
                p = request.end_time.split(":")
                config.end_time = time(int(p[0]), int(p[1]))
            else:
                config.end_time = request.end_time
        if request.period_duration_minutes:
            config.period_duration_minutes = request.period_duration_minutes
        if request.periods_per_day:
            config.periods_per_day = request.periods_per_day
        if request.break_after_period is not None:
            config.break_after_period = request.break_after_period
        if request.break_duration_minutes is not None:
            config.break_duration_minutes = request.break_duration_minutes
        if request.lunch_after_period is not None:
            config.lunch_after_period = request.lunch_after_period
        if request.lunch_duration_minutes is not None:
            config.lunch_duration_minutes = request.lunch_duration_minutes

        return config

    def _build_requirements(
        self,
        assignments: List[TeacherAssignment],
        custom_reqs: Optional[List[SubjectRequirement]],
        distribution: Optional[dict] = None
    ) -> List[Dict[str, Any]]:
        """Determine required weekly periods per assigned subject."""
        custom_map = {r.subject_id: r for r in (custom_reqs or [])}
        dist = distribution or {}
        reqs = []

        # Deduplicate assignments by subject_id (take primary teacher)
        seen_subj = set()
        for a in assignments:
            if a.subject_id in seen_subj:
                continue
            seen_subj.add(a.subject_id)

            sub = a.subject
            t = a.teacher
            c_req = custom_map.get(a.subject_id)

            # Heuristic default periods per week based on subject
            periods = 4
            try:
                if sub and sub.name in dist:
                    periods = max(1, int(dist[sub.name]))
                elif str(a.subject_id) in dist:
                    periods = max(1, int(dist[str(a.subject_id)]))
                elif a.subject_id in dist:
                    periods = max(1, int(dist[a.subject_id]))
                elif c_req and c_req.periods_per_week:
                    periods = max(1, int(c_req.periods_per_week))
                elif sub:
                    name_lower = sub.name.lower()
                    if any(core in name_lower for core in ["math", "english", "somali", "arabic"]):
                        periods = 5
                    elif any(sci in name_lower for sci in ["physic", "chem", "bio", "science"]):
                        periods = 4
                    elif any(elec in name_lower for elec in ["islam", "geograph", "histor", "computer"]):
                        periods = 3
                    else:
                        periods = 2
            except (ValueError, TypeError):
                periods = 4

            reqs.append({
                "subject_id": a.subject_id,
                "subject_name": sub.name if sub else f"Subject {a.subject_id}",
                "teacher_id": c_req.teacher_id if (c_req and c_req.teacher_id) else (t.id if t else None),
                "teacher_name": t.full_name if t else "Staff",
                "periods_needed": periods
            })

        return reqs

    def _build_period_slots(self, config: TimetableSetting) -> List[Dict[str, Any]]:
        """Calculate start and end time for each period of the school day."""
        slots = []
        st = config.start_time
        if isinstance(st, str):
            p = st.split(":")
            st = time(int(p[0]), int(p[1]))
        curr = datetime.combine(datetime.today(), st)

        for p in range(1, config.periods_per_day + 1):
            start = curr.time()
            end_dt = curr + timedelta(minutes=config.period_duration_minutes)
            end = end_dt.time()

            slots.append({
                "period_number": p,
                "start_time": start,
                "end_time": end,
                "is_break": False,
                "name": f"Period {p}"
            })

            curr = end_dt

            # Check if break occurs after this period
            if config.break_after_period and p == config.break_after_period and config.break_duration_minutes > 0:
                curr += timedelta(minutes=config.break_duration_minutes)

            # Check if lunch occurs after this period
            if config.lunch_after_period and p == config.lunch_after_period and config.lunch_duration_minutes > 0:
                curr += timedelta(minutes=config.lunch_duration_minutes)

        return slots

    def _schedule_csp(
        self,
        school_class: SchoolClass,
        academic_year: str,
        days: List[str],
        period_slots: List[Dict[str, Any]],
        requirements: List[Dict[str, Any]],
        existing_other_slots: List[Timetable],
        teacher_avail_map: Dict[Tuple[int, str], TeacherAvailability],
        default_room: str
    ) -> Tuple[List[Dict[str, Any]], List[TimetableConflictDetail], List[str]]:
        """
        Constraint Satisfaction Engine to assign subjects and teachers to period grid.
        Enforces:
        - No teacher overlap across any classes.
        - Teacher availability compliance.
        - Daily subject limit (max 1 period per subject per day, max 2 if high frequency).
        - Maximum periods per day per teacher.
        """
        scheduled: List[Dict[str, Any]] = []
        conflicts: List[TimetableConflictDetail] = []
        unassigned: List[str] = []

        # Tracking state
        # (day, period_number) -> slot dict
        grid_occupied: Dict[Tuple[str, int], Dict[str, Any]] = {}

        # (day, teacher_id) -> list of start_times
        teacher_day_schedule: Dict[Tuple[str, int], List[Tuple[time, time]]] = {}
        # (day, room) -> list of start_times
        room_day_schedule: Dict[Tuple[str, str], List[Tuple[time, time]]] = {}

        # Populate with existing slots from other classes
        for s in existing_other_slots:
            d_key = s.day_of_week.lower()
            if s.teacher_id:
                t_key = (d_key, s.teacher_id)
                teacher_day_schedule.setdefault(t_key, []).append((s.start_time, s.end_time))
            if s.room:
                r_key = (d_key, s.room.lower().strip())
                room_day_schedule.setdefault(r_key, []).append((s.start_time, s.end_time))

        # (day, subject_id) -> count of periods scheduled on that day
        subject_day_count: Dict[Tuple[str, int], int] = {}
        # teacher_id -> total scheduled periods this week
        teacher_weekly_load: Dict[int, int] = {}

        # Sort requirements: prioritize subjects with highest periods needed (MRV heuristic)
        sorted_reqs = sorted(requirements, key=lambda r: r["periods_needed"], reverse=True)

        # Expanded list of lesson tokens to place
        tokens_to_place = []
        for req in sorted_reqs:
            for _ in range(req["periods_needed"]):
                tokens_to_place.append({
                    "subject_id": req["subject_id"],
                    "subject_name": req["subject_name"],
                    "teacher_id": req["teacher_id"],
                    "teacher_name": req["teacher_name"]
                })

        # Available grid cells: (day, period_slot)
        # Order days evenly across available days to spread workload
        all_cells = []
        for slot in period_slots:
            for day in days:
                all_cells.append((day, slot))

        for token in tokens_to_place:
            placed = False
            reasons_failed = []

            # Find best cell for this token
            # Preference: day where this subject is not yet taught today
            candidate_cells = sorted(
                all_cells,
                key=lambda c: (
                    subject_day_count.get((c[0], token["subject_id"]), 0),  # Spread across days
                    c[1]["period_number"]
                )
            )

            for day, slot in candidate_cells:
                cell_key = (day, slot["period_number"])
                if cell_key in grid_occupied:
                    continue  # already booked for this class

                # Constraint 1: Subject daily frequency cap (max 2 per day, preferred 1)
                curr_subj_day = subject_day_count.get((day, token["subject_id"]), 0)
                if curr_subj_day >= 2:
                    continue

                # Constraint 2: Teacher Availability
                teacher_id = token["teacher_id"]
                if teacher_id:
                    avail = teacher_avail_map.get((teacher_id, day.lower()))
                    if avail and not avail.is_available:
                        reasons_failed.append(f"Teacher {token['teacher_name']} is configured unavailable on {day}.")
                        continue

                    # Check max periods per day for teacher (default to full school day if not restricted)
                    max_day = avail.max_periods_per_day if (avail and avail.max_periods_per_day) else max(len(period_slots), 6)
                    curr_teacher_day_slots = teacher_day_schedule.get((day.lower(), teacher_id), [])
                    if len(curr_teacher_day_slots) >= max_day:
                        continue

                    # Check max periods per week for teacher (default to full school week if not restricted)
                    max_week = avail.max_periods_per_week if (avail and avail.max_periods_per_week) else max(len(period_slots) * len(days), 36)
                    if teacher_weekly_load.get(teacher_id, 0) >= max_week:
                        continue

                    # Constraint 3: Teacher collision with another class
                    has_teacher_collision = False
                    for t_start, t_end in curr_teacher_day_slots:
                        if slot["start_time"] < t_end and slot["end_time"] > t_start:
                            has_teacher_collision = True
                            reasons_failed.append(
                                f"Teacher {token['teacher_name']} has an overlapping class commitment on {day} ({t_start.strftime('%H:%M')}–{t_end.strftime('%H:%M')})."
                            )
                            break
                    if has_teacher_collision:
                        continue

                # Constraint 4: Room collision
                r_key = (day.lower(), default_room.lower().strip())
                curr_room_slots = room_day_schedule.get(r_key, [])
                has_room_collision = False
                for r_start, r_end in curr_room_slots:
                    if slot["start_time"] < r_end and slot["end_time"] > r_start:
                        has_room_collision = True
                        break
                if has_room_collision:
                    continue

                # Valid slot found! Place it!
                scheduled_item = {
                    "class_id": school_class.id,
                    "subject_id": token["subject_id"],
                    "subject_name": token["subject_name"],
                    "teacher_id": token["teacher_id"],
                    "teacher_name": token["teacher_name"],
                    "day_of_week": day,
                    "period_number": slot["period_number"],
                    "start_time": slot["start_time"],
                    "end_time": slot["end_time"],
                    "room": default_room,
                    "is_break": False
                }

                scheduled.append(scheduled_item)
                grid_occupied[cell_key] = scheduled_item
                subject_day_count[(day, token["subject_id"])] = curr_subj_day + 1

                if teacher_id:
                    teacher_day_schedule.setdefault((day.lower(), teacher_id), []).append(
                        (slot["start_time"], slot["end_time"])
                    )
                    teacher_weekly_load[teacher_id] = teacher_weekly_load.get(teacher_id, 0) + 1

                room_day_schedule.setdefault(r_key, []).append(
                    (slot["start_time"], slot["end_time"])
                )

                placed = True
                break

            if not placed:
                reason = reasons_failed[0] if reasons_failed else "All available periods in the weekly schedule are full."
                unassigned.append(f"{token['subject_name']} (Teacher: {token['teacher_name']}): {reason}")
                conflicts.append(TimetableConflictDetail(
                    conflict_type="UNAVAILABLE",
                    message=f"Cannot place period for '{token['subject_name']}': {reason}",
                    day_of_week=days[0] if days else "Monday",
                    start_time=period_slots[0]["start_time"].strftime('%H:%M'),
                    end_time=period_slots[0]["end_time"].strftime('%H:%M'),
                    class_name=school_class.name,
                    teacher_name=token["teacher_name"],
                    subject_name=token["subject_name"],
                    severity="WARNING"
                ))

        # Sort scheduled by day order, then start_time
        day_order = {d.lower(): idx for idx, d in enumerate(days)}
        scheduled.sort(key=lambda s: (day_order.get(s["day_of_week"].lower(), 99), s["start_time"]))

        return scheduled, conflicts, unassigned
