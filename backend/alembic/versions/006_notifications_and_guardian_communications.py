"""Create notifications and guardian communications tables

Revision ID: 006_notifications
Revises: 005_exam_paper_uploads
Create Date: 2026-09-17 11:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '006_notifications'
down_revision: Union[str, None] = '005_exam_paper_uploads'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Notification Templates Table
    op.create_table(
        'notification_templates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('title_template', sa.String(length=255), nullable=False),
        sa.Column('body_template', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='GENERAL'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code', name='uq_notification_template_code')
    )
    op.create_index(op.f('ix_notification_templates_id'), 'notification_templates', ['id'], unique=False)
    op.create_index(op.f('ix_notification_templates_code'), 'notification_templates', ['code'], unique=True)

    # 2. Notifications Table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=False),  # ATTENDANCE_ABSENT, RESULT_RELEASED, FEE_REMINDER, GENERAL_ANNOUNCEMENT, CUSTOM
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('channel', sa.String(length=50), nullable=False, server_default='SMS'),  # SMS, EMAIL, IN_APP, WHATSAPP
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),  # QUEUED, PENDING, SENT, DELIVERED, READ, FAILED, NOT_SENT, NOT_CONFIGURED
        sa.Column('failure_reason', sa.String(length=255), nullable=True),  # MISSING_CONTACT, INVALID_CONTACT, PROVIDER_UNAVAILABLE, PROVIDER_NOT_CONFIGURED
        
        # Recipient & Student Association
        sa.Column('student_id', sa.Integer(), nullable=True),
        sa.Column('guardian_name', sa.String(length=200), nullable=True),
        sa.Column('guardian_phone', sa.String(length=50), nullable=True),
        sa.Column('guardian_email', sa.String(length=255), nullable=True),
        sa.Column('guardian_relationship', sa.String(length=50), nullable=True),
        sa.Column('class_id', sa.Integer(), nullable=True),
        sa.Column('academic_year', sa.String(length=50), nullable=True),

        # Related Entity Linkage
        sa.Column('related_attendance_id', sa.Integer(), nullable=True),
        sa.Column('related_exam_id', sa.Integer(), nullable=True),
        sa.Column('related_result_id', sa.Integer(), nullable=True),
        sa.Column('related_release_batch_id', sa.Integer(), nullable=True),

        # Deduplication & Idempotency Key
        sa.Column('idempotency_key', sa.String(length=255), nullable=True),

        # Audit & State Timestamps
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('extra_data', sa.JSON(), nullable=True),

        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['related_attendance_id'], ['attendances.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['related_exam_id'], ['exams.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['related_result_id'], ['exam_results.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['related_release_batch_id'], ['result_release_batches.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('idempotency_key', name='uq_notifications_idempotency_key')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index(op.f('ix_notifications_notification_type'), 'notifications', ['notification_type'], unique=False)
    op.create_index(op.f('ix_notifications_status'), 'notifications', ['status'], unique=False)
    op.create_index(op.f('ix_notifications_channel'), 'notifications', ['channel'], unique=False)
    op.create_index(op.f('ix_notifications_student_id'), 'notifications', ['student_id'], unique=False)
    op.create_index(op.f('ix_notifications_class_id'), 'notifications', ['class_id'], unique=False)
    op.create_index(op.f('ix_notifications_created_at'), 'notifications', ['created_at'], unique=False)
    op.create_index(op.f('ix_notifications_idempotency_key'), 'notifications', ['idempotency_key'], unique=True)

    # 3. Notification Deliveries Table
    op.create_table(
        'notification_deliveries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('notification_id', sa.Integer(), nullable=False),
        sa.Column('channel', sa.String(length=50), nullable=False),
        sa.Column('recipient', sa.String(length=255), nullable=False),
        sa.Column('provider_name', sa.String(length=100), nullable=True),
        sa.Column('provider_message_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('error_code', sa.String(length=100), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('attempt_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_deliveries_id'), 'notification_deliveries', ['id'], unique=False)
    op.create_index(op.f('ix_notification_deliveries_notification_id'), 'notification_deliveries', ['notification_id'], unique=False)
    op.create_index(op.f('ix_notification_deliveries_status'), 'notification_deliveries', ['status'], unique=False)


def downgrade() -> None:
    op.drop_table('notification_deliveries')
    op.drop_table('notifications')
    op.drop_table('notification_templates')
