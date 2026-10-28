-- =============================================================================
-- Hawlwadaag Primary and Secondary School Management System
-- Module: Student Attendance Tracking Schema (PostgreSQL 14+)
-- Database: hawlwadaag_school_db
-- =============================================================================

CREATE TABLE IF NOT EXISTS attendances (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    teacher_id INTEGER REFERENCES teachers(id) ON DELETE SET NULL,
    academic_year VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    period VARCHAR(50),
    status VARCHAR(20) NOT NULL DEFAULT 'PRESENT',
    remarks VARCHAR(255),
    recorded_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_date_subject_period UNIQUE (student_id, date, subject_id, period)
);

CREATE INDEX IF NOT EXISTS ix_attendances_id ON attendances(id);
CREATE INDEX IF NOT EXISTS ix_attendances_student_id ON attendances(student_id);
CREATE INDEX IF NOT EXISTS ix_attendances_class_id ON attendances(class_id);
CREATE INDEX IF NOT EXISTS ix_attendances_subject_id ON attendances(subject_id);
CREATE INDEX IF NOT EXISTS ix_attendances_teacher_id ON attendances(teacher_id);
CREATE INDEX IF NOT EXISTS ix_attendances_academic_year ON attendances(academic_year);
CREATE INDEX IF NOT EXISTS ix_attendances_date ON attendances(date);
CREATE INDEX IF NOT EXISTS ix_attendances_status ON attendances(status);
