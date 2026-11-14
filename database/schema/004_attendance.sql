-- =============================================================================
-- Hawlwadaag Primary and Secondary School Management System
-- Module: Student Attendance Tracking Schema (PostgreSQL 14+)
-- Database: hawlwadaag_school_db
-- =============================================================================

CREATE TABLE IF NOT EXISTS attendance_submissions (
    id SERIAL PRIMARY KEY,
    academic_year VARCHAR(50) NOT NULL,
    class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    period VARCHAR(50),
    teacher_id INTEGER REFERENCES teachers(id) ON DELETE SET NULL,
    submitted_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'SUBMITTED',
    total_students INTEGER NOT NULL DEFAULT 0,
    present_count INTEGER NOT NULL DEFAULT 0,
    late_count INTEGER NOT NULL DEFAULT 0,
    absent_count INTEGER NOT NULL DEFAULT 0,
    submission_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_attendance_submission_session UNIQUE NULLS NOT DISTINCT (class_id, subject_id, date, period)
);

CREATE INDEX IF NOT EXISTS ix_attendance_submissions_id ON attendance_submissions(id);
CREATE INDEX IF NOT EXISTS ix_attendance_submissions_class_id ON attendance_submissions(class_id);
CREATE INDEX IF NOT EXISTS ix_attendance_submissions_subject_id ON attendance_submissions(subject_id);
CREATE INDEX IF NOT EXISTS ix_attendance_submissions_date ON attendance_submissions(date);
CREATE INDEX IF NOT EXISTS ix_attendance_submissions_academic_year ON attendance_submissions(academic_year);
CREATE INDEX IF NOT EXISTS ix_attendance_submissions_teacher_id ON attendance_submissions(teacher_id);

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
    CONSTRAINT uq_student_date_subject_period UNIQUE NULLS NOT DISTINCT (student_id, date, subject_id, period)
);

CREATE INDEX IF NOT EXISTS ix_attendances_id ON attendances(id);
CREATE INDEX IF NOT EXISTS ix_attendances_student_id ON attendances(student_id);
CREATE INDEX IF NOT EXISTS ix_attendances_class_id ON attendances(class_id);
CREATE INDEX IF NOT EXISTS ix_attendances_subject_id ON attendances(subject_id);
CREATE INDEX IF NOT EXISTS ix_attendances_teacher_id ON attendances(teacher_id);
CREATE INDEX IF NOT EXISTS ix_attendances_academic_year ON attendances(academic_year);
CREATE INDEX IF NOT EXISTS ix_attendances_date ON attendances(date);
CREATE INDEX IF NOT EXISTS ix_attendances_status ON attendances(status);
