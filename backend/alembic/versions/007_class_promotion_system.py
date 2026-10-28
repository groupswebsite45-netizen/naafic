"""Create class promotion batches and records tables

Revision ID: 007_class_promotions
Revises: 006_notifications
Create Date: 2026-09-17 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '007_class_promotions'
down_revision: Union[str, None] = '006_notifications'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Class Promotion Batches Table
    op.create_table(
        'class_promotion_batches',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('batch_code', sa.String(length=50), nullable=False),
        sa.Column('source_academic_year', sa.String(length=50), nullable=False),
        sa.Column('target_academic_year', sa.String(length=50), nullable=False),
        sa.Column('promotion_type', sa.String(length=30), nullable=False, server_default='BULK_PROMOTION'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='COMPLETED'),
        sa.Column('total_promoted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_graduated', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_skipped', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('batch_code', name='uq_class_promotion_batch_code')
    )
    op.create_index(op.f('ix_class_promotion_batches_id'), 'class_promotion_batches', ['id'], unique=False)
    op.create_index(op.f('ix_class_promotion_batches_batch_code'), 'class_promotion_batches', ['batch_code'], unique=True)
    op.create_index(op.f('ix_class_promotion_batches_source_academic_year'), 'class_promotion_batches', ['source_academic_year'], unique=False)
    op.create_index(op.f('ix_class_promotion_batches_target_academic_year'), 'class_promotion_batches', ['target_academic_year'], unique=False)
    op.create_index(op.f('ix_class_promotion_batches_status'), 'class_promotion_batches', ['status'], unique=False)
    op.create_index(op.f('ix_class_promotion_batches_created_by_id'), 'class_promotion_batches', ['created_by_id'], unique=False)
    op.create_index(op.f('ix_class_promotion_batches_created_at'), 'class_promotion_batches', ['created_at'], unique=False)

    # 2. Class Promotion Records Table
    op.create_table(
        'class_promotion_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('from_class_id', sa.Integer(), nullable=True),
        sa.Column('to_class_id', sa.Integer(), nullable=True),
        sa.Column('from_enrollment_id', sa.Integer(), nullable=True),
        sa.Column('to_enrollment_id', sa.Integer(), nullable=True),
        sa.Column('source_academic_year', sa.String(length=50), nullable=False),
        sa.Column('target_academic_year', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=30), nullable=False, server_default='PROMOTED'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='COMPLETED'),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['batch_id'], ['class_promotion_batches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['from_class_id'], ['classes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['to_class_id'], ['classes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['from_enrollment_id'], ['student_enrollments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['to_enrollment_id'], ['student_enrollments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_class_promotion_records_id'), 'class_promotion_records', ['id'], unique=False)
    op.create_index(op.f('ix_class_promotion_records_batch_id'), 'class_promotion_records', ['batch_id'], unique=False)
    op.create_index(op.f('ix_class_promotion_records_student_id'), 'class_promotion_records', ['student_id'], unique=False)
    op.create_index(op.f('ix_class_promotion_records_from_class_id'), 'class_promotion_records', ['from_class_id'], unique=False)
    op.create_index(op.f('ix_class_promotion_records_to_class_id'), 'class_promotion_records', ['to_class_id'], unique=False)


def downgrade() -> None:
    op.drop_table('class_promotion_records')
    op.drop_table('class_promotion_batches')
