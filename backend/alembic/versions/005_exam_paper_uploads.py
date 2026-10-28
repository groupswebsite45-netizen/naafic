"""Add exam paper upload metadata to exam_results

Revision ID: 005_exam_paper_uploads
Revises: 004_attendance_tracking
Create Date: 2026-09-16 15:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '005_exam_paper_uploads'
down_revision: Union[str, None] = '004_attendance_tracking'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('exam_results', sa.Column('paper_file_path', sa.String(length=500), nullable=True))
    op.add_column('exam_results', sa.Column('paper_original_name', sa.String(length=255), nullable=True))
    op.add_column('exam_results', sa.Column('paper_mime_type', sa.String(length=100), nullable=True))
    op.add_column('exam_results', sa.Column('paper_file_size', sa.Integer(), nullable=True))
    op.add_column('exam_results', sa.Column('paper_uploaded_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('exam_results', 'paper_uploaded_at')
    op.drop_column('exam_results', 'paper_file_size')
    op.drop_column('exam_results', 'paper_mime_type')
    op.drop_column('exam_results', 'paper_original_name')
    op.drop_column('exam_results', 'paper_file_path')
