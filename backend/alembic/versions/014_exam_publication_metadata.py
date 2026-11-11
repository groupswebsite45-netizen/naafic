"""Add published_at and published_by_id to exams table for exam publication workflow

Revision ID: 014_exam_publication_metadata
Revises: 013_student_profile_photos
Create Date: 2026-11-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '014_exam_publication_metadata'
down_revision = '013_student_profile_photos'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add published_at timestamp
    op.add_column(
        'exams',
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True)
    )
    # Add published_by_id foreign key
    op.add_column(
        'exams',
        sa.Column('published_by_id', sa.Integer(), nullable=True)
    )
    # Add index and foreign key constraint
    op.create_index(op.f('ix_exams_published_at'), 'exams', ['published_at'], unique=False)
    op.create_foreign_key(
        'fk_exams_published_by_id',
        'exams',
        'users',
        ['published_by_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_exams_published_by_id', 'exams', type_='foreignkey')
    op.drop_index(op.f('ix_exams_published_at'), table_name='exams')
    op.drop_column('exams', 'published_by_id')
    op.drop_column('exams', 'published_at')

