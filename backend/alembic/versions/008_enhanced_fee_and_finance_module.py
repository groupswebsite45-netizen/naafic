"""enhanced fee and finance module

Revision ID: 008_enhanced_fee_finance
Revises: 007_class_promotions
Create Date: 2026-09-17 15:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008_enhanced_fee_finance'
down_revision = '007_class_promotions'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add frequency to fee_structures
    op.add_column(
        'fee_structures',
        sa.Column('frequency', sa.String(length=50), server_default='Term', nullable=False)
    )

    # 2. Add invoice_number, academic_year, class_id, fee_type to student_fees
    op.add_column(
        'student_fees',
        sa.Column('invoice_number', sa.String(length=50), nullable=True)
    )
    op.add_column(
        'student_fees',
        sa.Column('academic_year', sa.String(length=50), nullable=True)
    )
    op.add_column(
        'student_fees',
        sa.Column('class_id', sa.Integer(), nullable=True)
    )
    op.add_column(
        'student_fees',
        sa.Column('fee_type', sa.String(length=100), nullable=True)
    )
    op.create_foreign_key(
        'fk_student_fees_class_id_classes',
        'student_fees',
        'classes',
        ['class_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # 3. Add status to fee_payments
    op.add_column(
        'fee_payments',
        sa.Column('status', sa.String(length=20), server_default='VERIFIED', nullable=False)
    )

    # 4. Backfill existing student_fees with invoice numbers and academic year
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE student_fees sf
        SET invoice_number = 'INV-2026-' || LPAD(sf.id::text, 6, '0'),
            academic_year = COALESCE(
                (SELECT fs.academic_year FROM fee_structures fs WHERE fs.id = sf.fee_structure_id),
                '2025-2026'
            ),
            class_id = (SELECT fs.class_id FROM fee_structures fs WHERE fs.id = sf.fee_structure_id),
            fee_type = (SELECT fs.name FROM fee_structures fs WHERE fs.id = sf.fee_structure_id)
        WHERE sf.invoice_number IS NULL;
    """))

    # Now enforce NOT NULL and UNIQUE on invoice_number
    op.alter_column('student_fees', 'invoice_number', nullable=False)
    op.alter_column('student_fees', 'academic_year', nullable=False)
    op.create_index(op.f('ix_student_fees_invoice_number'), 'student_fees', ['invoice_number'], unique=True)
    op.create_index(op.f('ix_student_fees_academic_year'), 'student_fees', ['academic_year'], unique=False)
    op.create_index(op.f('ix_student_fees_class_id'), 'student_fees', ['class_id'], unique=False)
    op.create_index(op.f('ix_fee_payments_status'), 'fee_payments', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_fee_payments_status'), table_name='fee_payments')
    op.drop_column('fee_payments', 'status')

    op.drop_index(op.f('ix_student_fees_class_id'), table_name='student_fees')
    op.drop_index(op.f('ix_student_fees_academic_year'), table_name='student_fees')
    op.drop_index(op.f('ix_student_fees_invoice_number'), table_name='student_fees')
    op.drop_constraint('fk_student_fees_class_id_classes', 'student_fees', type_='foreignkey')
    op.drop_column('student_fees', 'fee_type')
    op.drop_column('student_fees', 'class_id')
    op.drop_column('student_fees', 'academic_year')
    op.drop_column('student_fees', 'invoice_number')

    op.drop_column('fee_structures', 'frequency')
