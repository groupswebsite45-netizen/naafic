"""Add attendance tracking module

Revision ID: 004_attendance_tracking
Revises: 003_result_workflow_and_releases
Create Date: 2026-09-16 14:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '004_attendance_tracking'
down_revision: Union[str, None] = '003_result_workflow_and_releases'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'attendances',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('class_id', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=True),
        sa.Column('academic_year', sa.String(length=50), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('period', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='PRESENT', nullable=False),
        sa.Column('remarks', sa.String(length=255), nullable=True),
        sa.Column('recorded_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['recorded_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id', 'date', 'subject_id', 'period', name='uq_student_date_subject_period')
    )
    op.create_index(op.f('ix_attendances_id'), 'attendances', ['id'], unique=False)
    op.create_index(op.f('ix_attendances_student_id'), 'attendances', ['student_id'], unique=False)
    op.create_index(op.f('ix_attendances_class_id'), 'attendances', ['class_id'], unique=False)
    op.create_index(op.f('ix_attendances_subject_id'), 'attendances', ['subject_id'], unique=False)
    op.create_index(op.f('ix_attendances_teacher_id'), 'attendances', ['teacher_id'], unique=False)
    op.create_index(op.f('ix_attendances_academic_year'), 'attendances', ['academic_year'], unique=False)
    op.create_index(op.f('ix_attendances_date'), 'attendances', ['date'], unique=False)
    op.create_index(op.f('ix_attendances_status'), 'attendances', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_attendances_status'), table_name='attendances')
    op.drop_index(op.f('ix_attendances_date'), table_name='attendances')
    op.drop_index(op.f('ix_attendances_academic_year'), table_name='attendances')
    op.drop_index(op.f('ix_attendances_teacher_id'), table_name='attendances')
    op.drop_index(op.f('ix_attendances_subject_id'), table_name='attendances')
    op.drop_index(op.f('ix_attendances_class_id'), table_name='attendances')
    op.drop_index(op.f('ix_attendances_student_id'), table_name='attendances')
    op.drop_index(op.f('ix_attendances_id'), table_name='attendances')
    op.drop_table('attendances')
