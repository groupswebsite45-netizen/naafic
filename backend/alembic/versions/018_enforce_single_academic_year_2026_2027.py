"""Enforce single academic year 2026/2027 across system

Revision ID: 018_enforce_academic_year_2026_2027
Revises: 017_prevent_dup_attendance
Create Date: 2026-11-14 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '018_single_academic_year_2026'
down_revision = '017_prevent_dup_attendance'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    def safe_update(table: str, sql: str):
        exists = conn.execute(text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table}')")).scalar()
        if exists:
            conn.execute(text(sql))

    safe_update("system_settings", "UPDATE system_settings SET value = '2026/2027' WHERE key = 'academic_year_current'")
    safe_update("notifications", "UPDATE notifications SET academic_year = '2026/2027' WHERE academic_year != '2026/2027' OR academic_year IS NULL")
    safe_update("student_result_views", "UPDATE student_result_views SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'")
    safe_update("fee_structures", "UPDATE fee_structures SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'")
    safe_update("student_fees", "UPDATE student_fees SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'")
    safe_update("teacher_availabilities", "UPDATE teacher_availabilities SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'")
    safe_update("student_import_logs", "UPDATE student_import_logs SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'")
    safe_update("class_promotion_batches", "UPDATE class_promotion_batches SET source_academic_year = '2026/2027', target_academic_year = '2026/2027' WHERE source_academic_year != '2026/2027' OR target_academic_year != '2026/2027'")
    safe_update("class_promotion_records", "UPDATE class_promotion_records SET source_academic_year = '2026/2027', target_academic_year = '2026/2027' WHERE source_academic_year != '2026/2027' OR target_academic_year != '2026/2027'")
    safe_update("result_release_batches", "UPDATE result_release_batches SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'")
    safe_update("result_submissions", "UPDATE result_submissions SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'")
    safe_update("attendance_submissions", "UPDATE attendance_submissions SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'")
    safe_update("teacher_attendances", "UPDATE teacher_attendances SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'")
    safe_update("timetable_settings", "UPDATE timetable_settings SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'")
    safe_update("timetables", "UPDATE timetables SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'")
    safe_update("exams", "UPDATE exams SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'")
    safe_update("attendances", "UPDATE attendances SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'")
    safe_update("teacher_assignments", "UPDATE teacher_assignments SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'")
    safe_update("student_enrollments", "UPDATE student_enrollments SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'")
    safe_update("classes", "UPDATE classes SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'")


def downgrade() -> None:
    pass
