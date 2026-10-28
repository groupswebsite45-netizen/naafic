"""Seed script for Student Attendance records in PostgreSQL."""
import os
import sys
from datetime import date, timedelta

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.database import SessionLocal
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.student_enrollment import StudentEnrollment
from app.models.timetable import Timetable


def seed_attendance():
    db = SessionLocal()
    try:
        # Check if already seeded
        existing_count = db.query(Attendance).count()
        if existing_count > 0:
            print(f"Attendance already seeded ({existing_count} records found). Skipping.")
            return

        print("Seeding attendance records for enrolled students...")

        # Target Student 1 (Mustaf Yusuf, id=1, class=7) and Student 2 (Amina Ibrahim, id=2, class=7)
        # Class 7 subjects:
        # 1: Mathematics (Ahmed Ali)
        # 3: English Language (Fadumo Warsame)
        # 4: Arabic & Islamic Studies (Sheikh Abdirahman)
        # 5: Integrated Science (Khadija Guled)
        # 10: ICT & Computer Studies (Abdi Farah)
        # 2: Somali Language & Literature (Fadumo Warsame)

        # Generate records over 8 weeks leading up to today (2026-09-16)
        base_date = date(2026, 7, 20)  # Monday
        academic_year = "2025-2026"

        # Schedule template per week:
        # (day_offset, subject_id, teacher_id, period)
        weekly_slots = [
            (0, 1, 1, "08:00 - 09:00"),   # Mon Math
            (0, 3, 2, "09:15 - 10:15"),   # Mon English
            (0, 4, 3, "10:30 - 11:30"),   # Mon Arabic/Islamic
            (1, 5, 4, "08:00 - 09:00"),   # Tue Science
            (1, 10, 5, "09:15 - 10:15"),  # Tue ICT
            (2, 2, 2, "08:00 - 09:00"),   # Wed Somali
        ]

        # For student 1: exactly 45 sessions:
        # Target: 42 Present, 3 Absent (Total: 45, 93.3% rate)
        # Absent on:
        # 1. Math on Week 2 (2026-07-27)
        # 2. Science on Week 4 (2026-08-11)
        # 3. Science on Week 6 (2026-08-25)
        # This yields: Math (10P, 1A), English (9P, 0A), Science (8P, 2A), ICT (8P, 0A), Somali (7P, 0A)

        total_sessions = 0
        records_to_insert = []

        for week in range(8):
            for day_offset, subj_id, t_id, period in weekly_slots:
                if total_sessions >= 45:
                    break

                sess_date = base_date + timedelta(days=(week * 7 + day_offset))
                if sess_date > date(2026, 9, 16):
                    continue

                total_sessions += 1

                # Determine Student 1 status
                s1_status = "PRESENT"
                s1_remarks = "Attended on time"
                if subj_id == 1 and week == 1:
                    s1_status = "ABSENT"
                    s1_remarks = "Unexcused absence"
                elif subj_id == 5 and week == 3:
                    s1_status = "ABSENT"
                    s1_remarks = "Reported sick"
                elif subj_id == 5 and week == 5:
                    s1_status = "ABSENT"
                    s1_remarks = "Missed period"

                records_to_insert.append(
                    Attendance(
                        student_id=1,
                        class_id=7,
                        subject_id=subj_id,
                        teacher_id=t_id,
                        academic_year=academic_year,
                        date=sess_date,
                        period=period,
                        status=s1_status,
                        remarks=s1_remarks,
                        recorded_by_id=1
                    )
                )

                # Determine Student 2 status (different attendance record for IDOR verification)
                s2_status = "PRESENT"
                s2_remarks = "Attended"
                if subj_id == 5 and week == 2:
                    s2_status = "ABSENT"
                    s2_remarks = "Excused medical appointment"

                records_to_insert.append(
                    Attendance(
                        student_id=2,
                        class_id=7,
                        subject_id=subj_id,
                        teacher_id=t_id,
                        academic_year=academic_year,
                        date=sess_date,
                        period=period,
                        status=s2_status,
                        remarks=s2_remarks,
                        recorded_by_id=1
                    )
                )

        db.add_all(records_to_insert)
        db.commit()
        print(f"Successfully seeded {len(records_to_insert)} attendance records into PostgreSQL!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding attendance: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_attendance()
