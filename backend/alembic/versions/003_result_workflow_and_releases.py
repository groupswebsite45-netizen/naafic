"""Add result workflow models: result_submissions, result_release_batches, student_result_views, and alter exam_results

Revision ID: 003_result_workflow_and_releases
Revises: 002_school_management_modules
Create Date: 2026-09-16 13:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003_result_workflow_and_releases'
down_revision: Union[str, None] = '002_school_management_modules'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. result_submissions table
    op.create_table(
        'result_submissions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('exam_id', sa.Integer(), sa.ForeignKey('exams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('class_id', sa.Integer(), sa.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('subject_id', sa.Integer(), sa.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('teacher_id', sa.Integer(), sa.ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('academic_year', sa.String(length=50), nullable=False),
        sa.Column('exam_name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=30), server_default='DRAFT', nullable=False),
        sa.Column('expected_students', sa.Integer(), server_default='0', nullable=False),
        sa.Column('completed_students', sa.Integer(), server_default='0', nullable=False),
        sa.Column('pending_students', sa.Integer(), server_default='0', nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('submitted_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('returned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('return_reason', sa.Text(), nullable=True),
        sa.Column('submission_deadline', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('exam_id', 'class_id', 'subject_id', 'teacher_id', name='uq_result_sub_exam_class_subj_tch')
    )
    op.create_index(op.f('ix_result_submissions_id'), 'result_submissions', ['id'], unique=False)
    op.create_index(op.f('ix_result_submissions_exam_id'), 'result_submissions', ['exam_id'], unique=False)
    op.create_index(op.f('ix_result_submissions_class_id'), 'result_submissions', ['class_id'], unique=False)
    op.create_index(op.f('ix_result_submissions_subject_id'), 'result_submissions', ['subject_id'], unique=False)
    op.create_index(op.f('ix_result_submissions_teacher_id'), 'result_submissions', ['teacher_id'], unique=False)
    op.create_index(op.f('ix_result_submissions_academic_year'), 'result_submissions', ['academic_year'], unique=False)
    op.create_index(op.f('ix_result_submissions_exam_name'), 'result_submissions', ['exam_name'], unique=False)
    op.create_index(op.f('ix_result_submissions_status'), 'result_submissions', ['status'], unique=False)

    # 2. result_release_batches table
    op.create_table(
        'result_release_batches',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('batch_code', sa.String(length=50), nullable=False),
        sa.Column('exam_name', sa.String(length=100), nullable=False),
        sa.Column('academic_year', sa.String(length=50), nullable=False),
        sa.Column('class_id', sa.Integer(), sa.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('release_type', sa.String(length=20), server_default='FULL', nullable=False),
        sa.Column('status', sa.String(length=20), server_default='RELEASED', nullable=False),
        sa.Column('released_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('released_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('results_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('batch_code')
    )
    op.create_index(op.f('ix_result_release_batches_id'), 'result_release_batches', ['id'], unique=False)
    op.create_index(op.f('ix_result_release_batches_batch_code'), 'result_release_batches', ['batch_code'], unique=True)
    op.create_index(op.f('ix_result_release_batches_exam_name'), 'result_release_batches', ['exam_name'], unique=False)
    op.create_index(op.f('ix_result_release_batches_academic_year'), 'result_release_batches', ['academic_year'], unique=False)
    op.create_index(op.f('ix_result_release_batches_class_id'), 'result_release_batches', ['class_id'], unique=False)
    op.create_index(op.f('ix_result_release_batches_released_at'), 'result_release_batches', ['released_at'], unique=False)

    # 3. student_result_views table
    op.create_table(
        'student_result_views',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('student_id', sa.Integer(), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),
        sa.Column('exam_name', sa.String(length=100), nullable=False),
        sa.Column('class_id', sa.Integer(), sa.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('academic_year', sa.String(length=50), nullable=False),
        sa.Column('release_batch_id', sa.Integer(), sa.ForeignKey('result_release_batches.id', ondelete='SET NULL'), nullable=True),
        sa.Column('first_viewed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_viewed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('view_count', sa.Integer(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id', 'exam_name', 'class_id', 'academic_year', name='uq_student_exam_class_year_view')
    )
    op.create_index(op.f('ix_student_result_views_id'), 'student_result_views', ['id'], unique=False)
    op.create_index(op.f('ix_student_result_views_student_id'), 'student_result_views', ['student_id'], unique=False)
    op.create_index(op.f('ix_student_result_views_exam_name'), 'student_result_views', ['exam_name'], unique=False)
    op.create_index(op.f('ix_student_result_views_class_id'), 'student_result_views', ['class_id'], unique=False)
    op.create_index(op.f('ix_student_result_views_academic_year'), 'student_result_views', ['academic_year'], unique=False)

    # 4. Alter exam_results table to support workflow
    op.add_column('exam_results', sa.Column('class_id', sa.Integer(), nullable=True))
    op.add_column('exam_results', sa.Column('submission_id', sa.Integer(), nullable=True))
    op.add_column('exam_results', sa.Column('release_batch_id', sa.Integer(), nullable=True))
    op.add_column('exam_results', sa.Column('attendance_status', sa.String(length=20), server_default='PRESENT', nullable=False))
    op.add_column('exam_results', sa.Column('status', sa.String(length=20), server_default='DRAFT', nullable=False))
    op.alter_column('exam_results', 'marks_obtained', existing_type=sa.Numeric(precision=5, scale=2), nullable=True)

    op.create_index(op.f('ix_exam_results_class_id'), 'exam_results', ['class_id'], unique=False)
    op.create_index(op.f('ix_exam_results_submission_id'), 'exam_results', ['submission_id'], unique=False)
    op.create_index(op.f('ix_exam_results_release_batch_id'), 'exam_results', ['release_batch_id'], unique=False)
    op.create_index(op.f('ix_exam_results_status'), 'exam_results', ['status'], unique=False)

    op.create_foreign_key('fk_exam_results_class_id', 'exam_results', 'classes', ['class_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_exam_results_submission_id', 'exam_results', 'result_submissions', ['submission_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_exam_results_release_batch_id', 'exam_results', 'result_release_batches', ['release_batch_id'], ['id'], ondelete='SET NULL')

    # Backfill class_id on existing exam_results from exams.class_id
    op.execute("UPDATE exam_results SET class_id = exams.class_id FROM exams WHERE exam_results.exam_id = exams.id")


def downgrade() -> None:
    op.drop_constraint('fk_exam_results_release_batch_id', 'exam_results', type_='foreignkey')
    op.drop_constraint('fk_exam_results_submission_id', 'exam_results', type_='foreignkey')
    op.drop_constraint('fk_exam_results_class_id', 'exam_results', type_='foreignkey')
    op.drop_index(op.f('ix_exam_results_status'), table_name='exam_results')
    op.drop_index(op.f('ix_exam_results_release_batch_id'), table_name='exam_results')
    op.drop_index(op.f('ix_exam_results_submission_id'), table_name='exam_results')
    op.drop_index(op.f('ix_exam_results_class_id'), table_name='exam_results')
    op.alter_column('exam_results', 'marks_obtained', existing_type=sa.Numeric(precision=5, scale=2), nullable=False)
    op.drop_column('exam_results', 'status')
    op.drop_column('exam_results', 'attendance_status')
    op.drop_column('exam_results', 'release_batch_id')
    op.drop_column('exam_results', 'submission_id')
    op.drop_column('exam_results', 'class_id')

    op.drop_table('student_result_views')
    op.drop_table('result_release_batches')
    op.drop_table('result_submissions')
