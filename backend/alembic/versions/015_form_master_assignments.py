"""Add form_master_assignments table for Admin-controlled Form Master management

Revision ID: 015_form_master_assignments
Revises: 014_exam_publication_metadata
Create Date: 2026-11-13 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '015_form_master_assignments'
down_revision = '014_exam_publication_metadata'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'form_master_assignments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('class_id', sa.Integer(), nullable=False),
        sa.Column('academic_year', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='ACTIVE', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('appointed_by_id', sa.Integer(), nullable=True),
        sa.Column('appointed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('revoked_by_id', sa.Integer(), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['appointed_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['revoked_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_form_master_assignments_id'), 'form_master_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_form_master_assignments_teacher_id'), 'form_master_assignments', ['teacher_id'], unique=False)
    op.create_index(op.f('ix_form_master_assignments_class_id'), 'form_master_assignments', ['class_id'], unique=False)
    op.create_index(op.f('ix_form_master_assignments_academic_year'), 'form_master_assignments', ['academic_year'], unique=False)
    op.create_index(op.f('ix_form_master_assignments_status'), 'form_master_assignments', ['status'], unique=False)
    op.create_index('ix_form_master_class_year_status', 'form_master_assignments', ['class_id', 'academic_year', 'status'], unique=False)
    op.create_index('ix_form_master_teacher_year_status', 'form_master_assignments', ['teacher_id', 'academic_year', 'status'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_form_master_teacher_year_status', table_name='form_master_assignments')
    op.drop_index('ix_form_master_class_year_status', table_name='form_master_assignments')
    op.drop_index(op.f('ix_form_master_assignments_status'), table_name='form_master_assignments')
    op.drop_index(op.f('ix_form_master_assignments_academic_year'), table_name='form_master_assignments')
    op.drop_index(op.f('ix_form_master_assignments_class_id'), table_name='form_master_assignments')
    op.drop_index(op.f('ix_form_master_assignments_teacher_id'), table_name='form_master_assignments')
    op.drop_index(op.f('ix_form_master_assignments_id'), table_name='form_master_assignments')
    op.drop_table('form_master_assignments')

