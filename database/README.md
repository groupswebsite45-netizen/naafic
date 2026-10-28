# Hawlwadaag School Management System - Database Documentation

PostgreSQL database: `hawlwadaag_school_db`  
ORM: SQLAlchemy (Async / Sync Session pool with connection recycling)  
Migration Engine: Alembic

---

## Complete Table Schema Reference

### 1. `users`
- **Purpose**: Unified system users for Admin, Faculty, and Students with bcrypt-hashed credentials.
- **Primary Key**: `id` (Integer, autoincrement)
- **Important Fields**:
  - `email` (VARCHAR 255, UNIQUE, NOT NULL)
  - `username` (VARCHAR 100, UNIQUE, NOT NULL)
  - `hashed_password` (VARCHAR 255, NOT NULL)
  - `full_name` (VARCHAR 200, NOT NULL)
  - `phone_number` (VARCHAR 50, nullable)
  - `is_active` (BOOLEAN, default True)
  - `is_superuser` (BOOLEAN, default False)
  - `last_login_at` (TIMESTAMP WITH TIME ZONE)
  - `created_at`, `updated_at`
- **Relationships**:
  - `user_roles` -> `user_roles.user_id` (1:N)
  - `sessions` -> `sessions.user_id` (1:N)
  - `teacher_profile` -> `teachers.user_id` (1:1)
  - `student_profile` -> `students.user_id` (1:1)

---

### 2. `roles` & `user_roles`
- **Purpose**: Role-Based Access Control (`ADMIN`, `TEACHER`, `STUDENT`).
- **Tables**:
  - `roles`: `id`, `name` (UNIQUE), `description`, `created_at`
  - `user_roles`: `id`, `user_id` (FK `users.id`), `role_id` (FK `roles.id`), `assigned_by_id` (FK `users.id`), `created_at`

---

### 3. `classes`
- **Purpose**: Primary & Secondary grade levels, sections, and classroom capacities.
- **Primary Key**: `id` (Integer, autoincrement)
- **Important Fields**:
  - `name` (VARCHAR 100, NOT NULL, indexed) - e.g., "Grade 1", "Grade 7", "Form 4"
  - `code` (VARCHAR 50, UNIQUE, NOT NULL, indexed) - e.g., "G7-A", "G8-B"
  - `section` (VARCHAR 50, nullable)
  - `academic_year` (VARCHAR 50, NOT NULL, indexed) - e.g., "2025-2026"
  - `capacity` (INTEGER, default 40)
  - `description` (TEXT)
  - `status` (VARCHAR 20, default "ACTIVE")
- **Relationships**:
  - `enrollments` -> `student_enrollments.class_id`
  - `teacher_assignments` -> `teacher_class_assignments.class_id`
  - `timetables` -> `timetables.class_id`
  - `fee_structures` -> `fee_structures.class_id`
  - `exams` -> `exams.class_id`

---

### 4. `subjects`
- **Purpose**: Curriculum academic disciplines and syllabus subject codes.
- **Primary Key**: `id` (Integer, autoincrement)
- **Important Fields**:
  - `name` (VARCHAR 100, NOT NULL) - e.g., "Mathematics", "Somali Language"
  - `code` (VARCHAR 50, UNIQUE, NOT NULL, indexed) - e.g., "MATH-101", "SOM-01"
  - `department` (VARCHAR 100) - e.g., "Languages", "Sciences", "Mathematics"
  - `description` (TEXT)
  - `status` (VARCHAR 20, default "ACTIVE")
- **Relationships**:
  - `teacher_assignments` -> `teacher_class_assignments.subject_id`
  - `timetables` -> `timetables.subject_id`
  - `exams` -> `exams.subject_id`

---

### 5. `teachers`
- **Purpose**: Faculty members and teaching staff records.
- **Primary Key**: `id` (Integer, autoincrement)
- **Foreign Keys**: `user_id` -> `users.id` (ON DELETE SET NULL, UNIQUE)
- **Important Fields**:
  - `teacher_number` (VARCHAR 50, UNIQUE, NOT NULL, indexed) - e.g., "TCH-1001"
  - `first_name`, `middle_name`, `last_name` (VARCHAR 100)
  - `gender` (VARCHAR 20, NOT NULL)
  - `date_of_birth` (DATE)
  - `phone` (VARCHAR 50)
  - `email` (VARCHAR 255, UNIQUE, NOT NULL)
  - `address` (TEXT)
  - `qualification` (VARCHAR 200)
  - `hire_date` (DATE)
  - `status` (VARCHAR 20, default "ACTIVE")
- **Relationships**:
  - `user` -> `users` (1:1)
  - `assignments` -> `teacher_class_assignments.teacher_id`
  - `timetables` -> `timetables.teacher_id`

---

### 6. `teacher_class_assignments`
- **Purpose**: Relational mapping of teachers to specific classes and subjects.
- **Primary Key**: `id` (Integer, autoincrement)
- **Foreign Keys**:
  - `teacher_id` -> `teachers.id` (ON DELETE CASCADE)
  - `class_id` -> `classes.id` (ON DELETE CASCADE)
  - `subject_id` -> `subjects.id` (ON DELETE CASCADE)
- **Constraints**:
  - `uq_teacher_class_subject_year`: Unique constraint on `(teacher_id, class_id, subject_id, academic_year)`

---

### 7. `students`
- **Purpose**: Student admissions, bio-data, and guardian contact details.
- **Primary Key**: `id` (Integer, autoincrement)
- **Foreign Keys**: `user_id` -> `users.id` (ON DELETE SET NULL, UNIQUE)
- **Important Fields**:
  - `admission_number` (VARCHAR 50, UNIQUE, NOT NULL, indexed) - e.g., "ADM-2026-001"
  - `first_name`, `middle_name`, `last_name` (VARCHAR 100)
  - `gender` (VARCHAR 20, NOT NULL)
  - `date_of_birth` (DATE)
  - `phone` (VARCHAR 50)
  - `address` (TEXT)
  - `guardian_name` (VARCHAR 200)
  - `guardian_phone` (VARCHAR 50)
  - `guardian_relationship` (VARCHAR 50)
  - `admission_date` (DATE)
  - `status` (VARCHAR 20, default "ACTIVE")
- **Relationships**:
  - `user` -> `users` (1:1)
  - `enrollments` -> `student_enrollments.student_id`
  - `student_fees` -> `student_fees.student_id`
  - `fee_payments` -> `fee_payments.student_id`
  - `exam_results` -> `exam_results.student_id`

---

### 8. `student_enrollments`
- **Purpose**: Historical and active class enrollment tracking across academic years.
- **Primary Key**: `id` (Integer, autoincrement)
- **Foreign Keys**:
  - `student_id` -> `students.id` (ON DELETE CASCADE)
  - `class_id` -> `classes.id` (ON DELETE CASCADE)
- **Important Fields**:
  - `academic_year` (VARCHAR 50, NOT NULL)
  - `roll_number` (VARCHAR 50)
  - `start_date`, `end_date` (DATE)
  - `status` (VARCHAR 20, default "ACTIVE")
- **Constraints**:
  - `uq_student_enrollment_year`: Unique constraint on `(student_id, class_id, academic_year)`

---

### 9. `timetables`
- **Purpose**: Weekly period scheduling with backend double-booking validation.
- **Primary Key**: `id` (Integer, autoincrement)
- **Foreign Keys**:
  - `class_id` -> `classes.id`
  - `subject_id` -> `subjects.id`
  - `teacher_id` -> `teachers.id`
- **Important Fields**:
  - `day_of_week` (VARCHAR 20, NOT NULL) - e.g., "Monday"
  - `start_time`, `end_time` (VARCHAR 10, NOT NULL) - e.g., "08:00", "08:45"
  - `room_number` (VARCHAR 50)
  - `academic_year` (VARCHAR 50, NOT NULL)
  - `status` (VARCHAR 20, default "ACTIVE")

---

### 10. `fee_structures`, `student_fees`, `fee_payments`
- **Purpose**: Finance, invoice billing, and payment ledger.
- **Tables**:
  - `fee_structures`: `id`, `name`, `academic_year`, `class_id` (FK nullable), `amount` (NUMERIC 10,2), `due_date`, `status`
  - `student_fees`: `id`, `student_id` (FK), `fee_structure_id` (FK), `academic_year`, `amount_due`, `amount_paid`, `balance`, `due_date`, `status` (`PAID`, `PARTIAL`, `UNPAID`)
  - `fee_payments`: `id`, `student_fee_id` (FK), `student_id` (FK), `amount`, `payment_date`, `payment_method` (`CASH`, `EVC_PLUS`, `ZAAD`, `SAHAL`, `BANK_TRANSFER`, `CHEQUE`), `reference_number`, `received_by`, `notes`

---

### 11. `exams` & `exam_results`
- **Purpose**: Assessments, examinations, and official student report card marks.
- **Tables**:
  - `exams`: `id`, `name`, `exam_type` (`MID_TERM`, `FINAL`, `QUIZ`, `ASSIGNMENT`), `academic_year`, `class_id` (FK), `subject_id` (FK), `total_marks` (INTEGER), `passing_marks` (INTEGER), `exam_date`, `start_time`, `end_time`, `status`
  - `exam_results`: `id`, `student_id` (FK), `exam_id` (FK), `subject_id` (FK), `marks_obtained` (NUMERIC 5,2), `total_marks`, `percentage` (NUMERIC 5,2), `grade`, `remarks`, `recorded_by_id` (FK `users.id`)
  - **Constraint**: `uq_student_exam_subject` on `(student_id, exam_id, subject_id)` prevents duplicate marks entries.

---

### 12. `sessions`, `audit_logs`, `system_settings`
- **Purpose**: JWT session invalidation registry, compliance audit logging, and dynamic branding settings.
