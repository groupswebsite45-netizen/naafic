"""Enforce unique teacher assignment per class, subject and academic year

Revision ID: 016_unique_assignments
Revises: 015_form_master_assignments
Create Date: 2026-11-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '016_unique_assignments'
down_revision = '015_form_master_assignments'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Safely replace the old unique constraint (uq_teacher_class_subject_year)
    # with the strict class + subject + academic_year constraint (uq_class_subject_academic_year)
    conn = op.get_bind()

    # Check existing constraints on teacher_assignments
    existing_constraints = {
        r[0] for r in conn.execute(sa.text("""
            SELECT conname
            FROM pg_constraint
            WHERE conrelid = 'teacher_assignments'::regclass
        """)).fetchall()
    }

    if 'uq_teacher_class_subject_year' in existing_constraints:
        op.drop_constraint('uq_teacher_class_subject_year', 'teacher_assignments', type_='unique')

    if 'uq_class_subject_academic_year' not in existing_constraints:
        op.create_unique_constraint(
            'uq_class_subject_academic_year',
            'teacher_assignments',
            ['class_id', 'subject_id', 'academic_year']
        )


def downgrade() -> None:
    conn = op.get_bind()
    existing_constraints = {
        r[0] for r in conn.execute(sa.text("""
            SELECT conname
            FROM pg_constraint
            WHERE conrelid = 'teacher_assignments'::regclass
        """)).fetchall()
    }

    if 'uq_class_subject_academic_year' in existing_constraints:
        op.drop_constraint('uq_class_subject_academic_year', 'teacher_assignments', type_='unique')

    if 'uq_teacher_class_subject_year' not in existing_constraints:
        op.create_unique_constraint(
            'uq_teacher_class_subject_year',
            'teacher_assignments',
            ['teacher_id', 'class_id', 'subject_id', 'academic_year']
        )

