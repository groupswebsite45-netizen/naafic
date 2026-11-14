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
    conn.execute(text("UPDATE system_settings SET value = '2026/2027' WHERE key = 'academic_year_current'"))
    conn.execute(text("UPDATE notifications SET academic_year = '2026/2027' WHERE academic_year != '2026/2027' OR academic_year IS NULL"))
    conn.execute(text("UPDATE student_result_views SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE fee_structures SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE student_fees SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE teacher_availabilities SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE student_import_logs SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE class_promotion_batches SET source_academic_year = '2026/2027', target_academic_year = '2026/2027' WHERE source_academic_year != '2026/2027' OR target_academic_year != '2026/2027'"))
    conn.execute(text("UPDATE class_promotion_records SET source_academic_year = '2026/2027', target_academic_year = '2026/2027' WHERE source_academic_year != '2026/2027' OR target_academic_year != '2026/2027'"))
    conn.execute(text("UPDATE result_release_batches SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE result_submissions SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE attendance_submissions SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE teacher_attendances SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE timetable_settings SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE timetables SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE exams SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE attendances SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE teacher_assignments SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE student_enrollments SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))
    conn.execute(text("UPDATE classes SET academic_year = '2026/2027' WHERE academic_year != '2026/2027'"))


def downgrade() -> None:
    pass
