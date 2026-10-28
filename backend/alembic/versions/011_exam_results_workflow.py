"""Add absence_reason, complaint to exam_results, and revisions, exam_type to result_submissions

Revision ID: 011_exam_results_workflow
Revises: 010_fee_struct_enhancements
Create Date: 2026-10-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011_exam_results_workflow'
down_revision = '010_fee_struct_enhancements'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add absence_reason and complaint to exam_results
    op.add_column(
        'exam_results',
        sa.Column('absence_reason', sa.Text(), nullable=True)
    )
    op.add_column(
        'exam_results',
        sa.Column('complaint', sa.Text(), nullable=True)
    )

    # 2. Add revisions and exam_type to result_submissions
    op.add_column(
        'result_submissions',
        sa.Column('revisions', sa.JSON(), nullable=True)
    )
    op.add_column(
        'result_submissions',
        sa.Column('exam_type', sa.String(length=50), nullable=True)
    )
    op.create_index(op.f('ix_result_submissions_exam_type'), 'result_submissions', ['exam_type'], unique=False)

    # 3. Backfill exam_type on result_submissions from exams table
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE result_submissions rs
        SET exam_type = e.exam_type
        FROM exams e
        WHERE rs.exam_id = e.id;
    """))


def downgrade() -> None:
    op.drop_index(op.f('ix_result_submissions_exam_type'), table_name='result_submissions')
    op.drop_column('result_submissions', 'exam_type')
    op.drop_column('result_submissions', 'revisions')
    op.drop_column('exam_results', 'complaint')
    op.drop_column('exam_results', 'absence_reason')
