"""Add timetable_settings, teacher_availabilities, and timetable enhancements

Revision ID: 012_advanced_timetable_system
Revises: 011_exam_results_workflow
Create Date: 2026-10-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '012_advanced_timetable_system'
down_revision = '011_exam_results_workflow'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create timetable_settings table
    op.create_table(
        'timetable_settings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('academic_year', sa.String(length=50), nullable=False),
        sa.Column('division', sa.String(length=20), server_default='ALL', nullable=False),
        sa.Column('school_days', sa.String(length=255), server_default='Saturday,Sunday,Monday,Tuesday,Wednesday,Thursday', nullable=False),
        sa.Column('start_time', sa.Time(), server_default='07:30:00', nullable=False),
        sa.Column('end_time', sa.Time(), server_default='13:30:00', nullable=False),
        sa.Column('period_duration_minutes', sa.Integer(), server_default='45', nullable=False),
        sa.Column('break_duration_minutes', sa.Integer(), server_default='20', nullable=False),
        sa.Column('break_after_period', sa.Integer(), server_default='3', nullable=False),
        sa.Column('lunch_duration_minutes', sa.Integer(), server_default='30', nullable=False),
        sa.Column('lunch_after_period', sa.Integer(), server_default='5', nullable=False),
        sa.Column('periods_per_day', sa.Integer(), server_default='6', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_timetable_settings_id'), 'timetable_settings', ['id'], unique=False)
    op.create_index(op.f('ix_timetable_settings_academic_year'), 'timetable_settings', ['academic_year'], unique=False)

    # 2. Create teacher_availabilities table
    op.create_table(
        'teacher_availabilities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('academic_year', sa.String(length=50), nullable=False),
        sa.Column('day_of_week', sa.String(length=20), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('end_time', sa.Time(), nullable=True),
        sa.Column('is_available', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('max_periods_per_day', sa.Integer(), server_default='5', nullable=True),
        sa.Column('max_periods_per_week', sa.Integer(), server_default='25', nullable=True),
        sa.Column('notes', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('teacher_id', 'academic_year', 'day_of_week', name='uq_teacher_year_day_availability')
    )
    op.create_index(op.f('ix_teacher_availabilities_id'), 'teacher_availabilities', ['id'], unique=False)
    op.create_index(op.f('ix_teacher_availabilities_teacher_id'), 'teacher_availabilities', ['teacher_id'], unique=False)
    op.create_index(op.f('ix_teacher_availabilities_academic_year'), 'teacher_availabilities', ['academic_year'], unique=False)
    op.create_index(op.f('ix_teacher_availabilities_day_of_week'), 'teacher_availabilities', ['day_of_week'], unique=False)

    # 3. Add columns to timetables table
    op.add_column('timetables', sa.Column('period_number', sa.Integer(), nullable=True))
    op.add_column('timetables', sa.Column('is_break', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('timetables', sa.Column('published_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('timetables', sa.Column('published_by_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_timetables_published_by_id', 'timetables', 'users', ['published_by_id'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('ix_timetables_period_number'), 'timetables', ['period_number'], unique=False)

    # Seed default timetable setting for active academic years if not present
    conn = op.get_bind()
    conn.execute(sa.text("""
        INSERT INTO timetable_settings (academic_year, division, school_days, start_time, end_time, period_duration_minutes, break_duration_minutes, break_after_period, lunch_duration_minutes, lunch_after_period, periods_per_day, is_active)
        VALUES ('2026/2027', 'ALL', 'Saturday,Sunday,Monday,Tuesday,Wednesday,Thursday', '07:30:00', '13:30:00', 45, 20, 3, 30, 5, 6, true)
        ON CONFLICT DO NOTHING;
    """))


def downgrade() -> None:
    op.drop_constraint('fk_timetables_published_by_id', 'timetables', type_='foreignkey')
    op.drop_index(op.f('ix_timetables_period_number'), table_name='timetables')
    op.drop_column('timetables', 'published_by_id')
    op.drop_column('timetables', 'published_at')
    op.drop_column('timetables', 'is_break')
    op.drop_column('timetables', 'period_number')

    op.drop_index(op.f('ix_teacher_availabilities_day_of_week'), table_name='teacher_availabilities')
    op.drop_index(op.f('ix_teacher_availabilities_academic_year'), table_name='teacher_availabilities')
    op.drop_index(op.f('ix_teacher_availabilities_teacher_id'), table_name='teacher_availabilities')
    op.drop_index(op.f('ix_teacher_availabilities_id'), table_name='teacher_availabilities')
    op.drop_table('teacher_availabilities')

    op.drop_index(op.f('ix_timetable_settings_academic_year'), table_name='timetable_settings')
    op.drop_index(op.f('ix_timetable_settings_id'), table_name='timetable_settings')
    op.drop_table('timetable_settings')
