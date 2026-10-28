"""Add school management modules: classes, subjects, teachers, students, enrollments, timetables, fees, exams

Revision ID: 002_school_management_modules
Revises: 001_initial_foundation
Create Date: 2026-09-16 09:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_school_management_modules'
down_revision: Union[str, None] = '001_initial_foundation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. classes table
    op.create_table(
        'classes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('section', sa.String(length=50), nullable=True),
        sa.Column('academic_year', sa.String(length=50), nullable=False),
        sa.Column('capacity', sa.Integer(), server_default='40', nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='ACTIVE', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_classes_id'), 'classes', ['id'], unique=False)
    op.create_index(op.f('ix_classes_name'), 'classes', ['name'], unique=False)
    op.create_index(op.f('ix_classes_code'), 'classes', ['code'], unique=True)
    op.create_index(op.f('ix_classes_academic_year'), 'classes', ['academic_year'], unique=False)

    # 2. subjects table
    op.create_table(
        'subjects',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='ACTIVE', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subjects_id'), 'subjects', ['id'], unique=False)
    op.create_index(op.f('ix_subjects_name'), 'subjects', ['name'], unique=False)
    op.create_index(op.f('ix_subjects_code'), 'subjects', ['code'], unique=True)

    # 3. teachers table
    op.create_table(
        'teachers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('teacher_number', sa.String(length=50), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('middle_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('gender', sa.String(length=20), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('qualification', sa.String(length=200), nullable=True),
        sa.Column('hire_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='ACTIVE', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teachers_id'), 'teachers', ['id'], unique=False)
    op.create_index(op.f('ix_teachers_user_id'), 'teachers', ['user_id'], unique=True)
    op.create_index(op.f('ix_teachers_teacher_number'), 'teachers', ['teacher_number'], unique=True)
    op.create_index(op.f('ix_teachers_email'), 'teachers', ['email'], unique=True)

    # 4. teacher_assignments table
    op.create_table(
        'teacher_assignments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('class_id', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('academic_year', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='ACTIVE', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('teacher_id', 'class_id', 'subject_id', 'academic_year', name='uq_teacher_class_subject_year')
    )
    op.create_index(op.f('ix_teacher_assignments_id'), 'teacher_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_teacher_assignments_teacher_id'), 'teacher_assignments', ['teacher_id'], unique=False)
    op.create_index(op.f('ix_teacher_assignments_class_id'), 'teacher_assignments', ['class_id'], unique=False)
    op.create_index(op.f('ix_teacher_assignments_subject_id'), 'teacher_assignments', ['subject_id'], unique=False)
    op.create_index(op.f('ix_teacher_assignments_academic_year'), 'teacher_assignments', ['academic_year'], unique=False)

    # 5. students table
    op.create_table(
        'students',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('admission_number', sa.String(length=50), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('middle_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('gender', sa.String(length=20), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('guardian_name', sa.String(length=200), nullable=True),
        sa.Column('guardian_phone', sa.String(length=50), nullable=True),
        sa.Column('guardian_email', sa.String(length=255), nullable=True),
        sa.Column('guardian_relationship', sa.String(length=50), nullable=True),
        sa.Column('admission_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='ACTIVE', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_students_id'), 'students', ['id'], unique=False)
    op.create_index(op.f('ix_students_user_id'), 'students', ['user_id'], unique=True)
    op.create_index(op.f('ix_students_admission_number'), 'students', ['admission_number'], unique=True)

    # 6. student_enrollments table
    op.create_table(
        'student_enrollments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('class_id', sa.Integer(), nullable=False),
        sa.Column('academic_year', sa.String(length=50), nullable=False),
        sa.Column('roll_number', sa.String(length=50), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='ACTIVE', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id', 'academic_year', name='uq_student_academic_year')
    )
    op.create_index(op.f('ix_student_enrollments_id'), 'student_enrollments', ['id'], unique=False)
    op.create_index(op.f('ix_student_enrollments_student_id'), 'student_enrollments', ['student_id'], unique=False)
    op.create_index(op.f('ix_student_enrollments_class_id'), 'student_enrollments', ['class_id'], unique=False)
    op.create_index(op.f('ix_student_enrollments_academic_year'), 'student_enrollments', ['academic_year'], unique=False)

    # 7. timetables table
    op.create_table(
        'timetables',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('class_id', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=True),
        sa.Column('academic_year', sa.String(length=50), nullable=False),
        sa.Column('day_of_week', sa.String(length=20), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('room', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='ACTIVE', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_timetables_id'), 'timetables', ['id'], unique=False)
    op.create_index(op.f('ix_timetables_class_id'), 'timetables', ['class_id'], unique=False)
    op.create_index(op.f('ix_timetables_subject_id'), 'timetables', ['subject_id'], unique=False)
    op.create_index(op.f('ix_timetables_teacher_id'), 'timetables', ['teacher_id'], unique=False)
    op.create_index(op.f('ix_timetables_academic_year'), 'timetables', ['academic_year'], unique=False)
    op.create_index(op.f('ix_timetables_day_of_week'), 'timetables', ['day_of_week'], unique=False)

    # 8. fee_structures table
    op.create_table(
        'fee_structures',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('academic_year', sa.String(length=50), nullable=False),
        sa.Column('class_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='ACTIVE', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fee_structures_id'), 'fee_structures', ['id'], unique=False)
    op.create_index(op.f('ix_fee_structures_name'), 'fee_structures', ['name'], unique=False)
    op.create_index(op.f('ix_fee_structures_academic_year'), 'fee_structures', ['academic_year'], unique=False)
    op.create_index(op.f('ix_fee_structures_class_id'), 'fee_structures', ['class_id'], unique=False)

    # 9. student_fees table
    op.create_table(
        'student_fees',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('fee_structure_id', sa.Integer(), nullable=False),
        sa.Column('amount_due', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('discount_amount', sa.Numeric(precision=10, scale=2), server_default='0.00', nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='PENDING', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['fee_structure_id'], ['fee_structures.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id', 'fee_structure_id', name='uq_student_fee_structure')
    )
    op.create_index(op.f('ix_student_fees_id'), 'student_fees', ['id'], unique=False)
    op.create_index(op.f('ix_student_fees_student_id'), 'student_fees', ['student_id'], unique=False)
    op.create_index(op.f('ix_student_fees_fee_structure_id'), 'student_fees', ['fee_structure_id'], unique=False)

    # 10. fee_payments table
    op.create_table(
        'fee_payments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('student_fee_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('receipt_number', sa.String(length=50), nullable=False),
        sa.Column('amount_paid', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('recorded_by_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['recorded_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['student_fee_id'], ['student_fees.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fee_payments_id'), 'fee_payments', ['id'], unique=False)
    op.create_index(op.f('ix_fee_payments_student_fee_id'), 'fee_payments', ['student_fee_id'], unique=False)
    op.create_index(op.f('ix_fee_payments_student_id'), 'fee_payments', ['student_id'], unique=False)
    op.create_index(op.f('ix_fee_payments_receipt_number'), 'fee_payments', ['receipt_number'], unique=True)

    # 11. exams table
    op.create_table(
        'exams',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('exam_type', sa.String(length=50), nullable=False),
        sa.Column('academic_year', sa.String(length=50), nullable=False),
        sa.Column('class_id', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('max_marks', sa.Numeric(precision=5, scale=2), server_default='100.00', nullable=False),
        sa.Column('pass_marks', sa.Numeric(precision=5, scale=2), server_default='50.00', nullable=False),
        sa.Column('status', sa.String(length=20), server_default='SCHEDULED', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exams_id'), 'exams', ['id'], unique=False)
    op.create_index(op.f('ix_exams_name'), 'exams', ['name'], unique=False)
    op.create_index(op.f('ix_exams_academic_year'), 'exams', ['academic_year'], unique=False)
    op.create_index(op.f('ix_exams_class_id'), 'exams', ['class_id'], unique=False)
    op.create_index(op.f('ix_exams_subject_id'), 'exams', ['subject_id'], unique=False)

    # 12. exam_results table
    op.create_table(
        'exam_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('exam_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('marks_obtained', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('grade', sa.String(length=5), nullable=True),
        sa.Column('remarks', sa.String(length=255), nullable=True),
        sa.Column('recorded_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['exam_id'], ['exams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recorded_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('exam_id', 'student_id', 'subject_id', name='uq_exam_student_subject')
    )
    op.create_index(op.f('ix_exam_results_id'), 'exam_results', ['id'], unique=False)
    op.create_index(op.f('ix_exam_results_exam_id'), 'exam_results', ['exam_id'], unique=False)
    op.create_index(op.f('ix_exam_results_student_id'), 'exam_results', ['student_id'], unique=False)
    op.create_index(op.f('ix_exam_results_subject_id'), 'exam_results', ['subject_id'], unique=False)


def downgrade() -> None:
    op.drop_table('exam_results')
    op.drop_table('exams')
    op.drop_table('fee_payments')
    op.drop_table('student_fees')
    op.drop_table('fee_structures')
    op.drop_table('timetables')
    op.drop_table('student_enrollments')
    op.drop_table('students')
    op.drop_table('teacher_assignments')
    op.drop_table('teachers')
    op.drop_table('subjects')
    op.drop_table('classes')
