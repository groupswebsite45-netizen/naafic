"""Add permanent student profile photo metadata to students table

Revision ID: 013_student_profile_photos
Revises: 012_advanced_timetable_system
Create Date: 2026-11-11 08:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '013_student_profile_photos'
down_revision: Union[str, None] = '012_advanced_timetable_system'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('students', sa.Column('photo_path', sa.String(length=500), nullable=True))
    op.add_column('students', sa.Column('photo_filename', sa.String(length=255), nullable=True))
    op.add_column('students', sa.Column('photo_mime_type', sa.String(length=100), nullable=True))
    op.add_column('students', sa.Column('photo_size', sa.Integer(), nullable=True))
    op.add_column('students', sa.Column('photo_uploaded_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('students', sa.Column('photo_updated_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('students', 'photo_updated_at')
    op.drop_column('students', 'photo_uploaded_at')
    op.drop_column('students', 'photo_size')
    op.drop_column('students', 'photo_mime_type')
    op.drop_column('students', 'photo_filename')
    op.drop_column('students', 'photo_path')
