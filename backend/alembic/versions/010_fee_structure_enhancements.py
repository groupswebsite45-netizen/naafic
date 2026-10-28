"""fee structure education level, creator, and uniqueness

Revision ID: 010_fee_structure_enhancements
Revises: 009_fee_struct_null
Create Date: 2026-09-19 11:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010_fee_struct_enhancements'
down_revision = '009_fee_struct_null'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add education_level to fee_structures
    op.add_column(
        'fee_structures',
        sa.Column('education_level', sa.String(length=20), nullable=True)
    )
    op.create_index(op.f('ix_fee_structures_education_level'), 'fee_structures', ['education_level'], unique=False)

    # 2. Add created_by_id to fee_structures
    op.add_column(
        'fee_structures',
        sa.Column('created_by_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_fee_structures_created_by_id_users',
        'fee_structures',
        'users',
        ['created_by_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_index(op.f('ix_fee_structures_created_by_id'), 'fee_structures', ['created_by_id'], unique=False)

    # 3. Backfill education_level for existing fee_structure 150 ("primary monthly fee")
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE fee_structures
        SET education_level = 'PRIMARY'
        WHERE id = 150 OR name ILIKE '%primary%';
    """))


def downgrade() -> None:
    op.drop_constraint('fk_fee_structures_created_by_id_users', 'fee_structures', type_='foreignkey')
    op.drop_index(op.f('ix_fee_structures_created_by_id'), table_name='fee_structures')
    op.drop_column('fee_structures', 'created_by_id')

    op.drop_index(op.f('ix_fee_structures_education_level'), table_name='fee_structures')
    op.drop_column('fee_structures', 'education_level')
