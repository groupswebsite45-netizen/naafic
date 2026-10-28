"""allow null fee_structure_id on delete set null

Revision ID: 009_fee_structure_ondelete_set_null
Revises: 008_enhanced_fee_finance
Create Date: 2026-09-19 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009_fee_struct_null'
down_revision = '008_enhanced_fee_finance'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('student_fees', 'fee_structure_id', nullable=True)
    try:
        op.drop_constraint('student_fees_fee_structure_id_fkey', 'student_fees', type_='foreignkey')
    except Exception:
        pass
    op.create_foreign_key(
        'student_fees_fee_structure_id_fkey',
        'student_fees', 'fee_structures',
        ['fee_structure_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('student_fees_fee_structure_id_fkey', 'student_fees', type_='foreignkey')
    op.create_foreign_key(
        'student_fees_fee_structure_id_fkey',
        'student_fees', 'fee_structures',
        ['fee_structure_id'], ['id'],
        ondelete='RESTRICT'
    )
    op.alter_column('student_fees', 'fee_structure_id', nullable=False)
