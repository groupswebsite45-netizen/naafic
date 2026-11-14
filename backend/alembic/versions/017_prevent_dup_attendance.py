"""Add attendance_submissions table and enforce strict uniqueness

Revision ID: 017_prevent_dup_attendance
Revises: 016_unique_assignments
Create Date: 2026-11-13 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '017_prevent_dup_attendance'
down_revision = '016_unique_assignments'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Create attendance_submissions table if not exists
    op.create_table(
        'attendance_submissions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('academic_year', sa.String(length=50), nullable=False),
        sa.Column('class_id', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('period', sa.String(length=50), nullable=True),
        sa.Column('teacher_id', sa.Integer(), nullable=True),
        sa.Column('submitted_by_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='SUBMITTED', nullable=False),
        sa.Column('total_students', sa.Integer(), server_default='0', nullable=False),
        sa.Column('present_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('late_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('absent_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('submission_time', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['submitted_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(op.f('ix_attendance_submissions_id'), 'attendance_submissions', ['id'], unique=False)
    op.create_index(op.f('ix_attendance_submissions_class_id'), 'attendance_submissions', ['class_id'], unique=False)
    op.create_index(op.f('ix_attendance_submissions_subject_id'), 'attendance_submissions', ['subject_id'], unique=False)
    op.create_index(op.f('ix_attendance_submissions_date'), 'attendance_submissions', ['date'], unique=False)
    op.create_index(op.f('ix_attendance_submissions_academic_year'), 'attendance_submissions', ['academic_year'], unique=False)
    op.create_index(op.f('ix_attendance_submissions_teacher_id'), 'attendance_submissions', ['teacher_id'], unique=False)

    # Add uniqueness constraint on attendance_submissions (session level) with NULLS NOT DISTINCT
    op.execute(
        "ALTER TABLE attendance_submissions ADD CONSTRAINT uq_attendance_submission_session "
        "UNIQUE NULLS NOT DISTINCT (class_id, subject_id, date, period);"
    )

    # 2. Backfill existing attendance records into attendance_submissions
    op.execute("""
        INSERT INTO attendance_submissions (
            academic_year, class_id, subject_id, date, period, teacher_id, submitted_by_id,
            total_students, present_count, late_count, absent_count, status, submission_time, created_at, updated_at
        )
        SELECT
            academic_year,
            class_id,
            subject_id,
            date,
            period,
            MAX(teacher_id) as teacher_id,
            MAX(recorded_by_id) as submitted_by_id,
            COUNT(id) as total_students,
            COUNT(CASE WHEN status = 'PRESENT' THEN 1 END) as present_count,
            COUNT(CASE WHEN status = 'LATE' THEN 1 END) as late_count,
            COUNT(CASE WHEN status IN ('ABSENT', 'EXCUSED') THEN 1 END) as absent_count,
            'SUBMITTED' as status,
            MIN(created_at) as submission_time,
            MIN(created_at) as created_at,
            MAX(updated_at) as updated_at
        FROM attendances
        GROUP BY academic_year, class_id, subject_id, date, period
        ON CONFLICT DO NOTHING;
    """)

    # 3. Upgrade attendances unique constraint to use NULLS NOT DISTINCT
    op.execute("ALTER TABLE attendances DROP CONSTRAINT IF EXISTS uq_student_date_subject_period;")
    op.execute(
        "ALTER TABLE attendances ADD CONSTRAINT uq_student_date_subject_period "
        "UNIQUE NULLS NOT DISTINCT (student_id, date, subject_id, period);"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE attendances DROP CONSTRAINT IF EXISTS uq_student_date_subject_period;")
    op.execute(
        "ALTER TABLE attendances ADD CONSTRAINT uq_student_date_subject_period "
        "UNIQUE (student_id, date, subject_id, period);"
    )
    op.drop_table('attendance_submissions')

