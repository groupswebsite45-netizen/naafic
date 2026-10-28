# Hawlwadaag Primary and Secondary School Management System

A production-grade, three-tier School Management System designed for Hawlwadaag Primary and Secondary School.

---

## System Architecture

```
hawlwadaag-school-management/
│
├── frontend/             # Vue 3, TypeScript, Pinia, Vite, Vanilla CSS
├── backend/              # FastAPI, SQLAlchemy, Pydantic, Alembic, PyJWT, Passlib
└── database/             # PostgreSQL schemas, Alembic migrations, ERD documentation
```

### Single Source of Truth
All real school data (Classes, Teachers, Students, Subjects, Timetable, Fees, Payments, Exams, Results, Users, Audit Logs) is strictly stored in local **PostgreSQL** (`hawlwadaag_school_db`).

---

## Modules Implemented

1. **Classes Management** (`/admin/classes`): Grade levels, sections, capacities, status.
2. **Subjects Management** (`/admin/subjects`): Curriculum subjects, departments, syllabus codes.
3. **Teachers Management** (`/admin/teachers`): Faculty records, portal account creation, class & subject assignments.
4. **Students Management** (`/admin/students`): Admissions, bio-data, historical enrollment transitions, guardian details, portal account creation.
5. **Timetable Management** (`/admin/timetable`): Weekly period scheduler with backend collision detection (teacher, class, room).
6. **Fee Management & Billing** (`/admin/fees`): Fee structures, student billing invoices, payment receipts (Cash, EVC Plus, ZAAD, Sahal, Bank), and balance calculations.
7. **Exams & Grading** (`/admin/exams`): Assessments, exams, marks entry, grades, and percentage computation.
8. **Teacher Portal** (`/teacher/*`): Faculty dashboard, assigned classes, students roster, weekly timetable, exam marks entry.
9. **Student Portal** (`/student/*`): Student dashboard, enrolled class & subjects, weekly timetable, fee invoice balance & receipt history, exam results.
10. **Admin Dashboard** (`/admin/dashboard`): Real-time metrics queried directly from PostgreSQL.

---

## How to Run Migrations

```bash
cd backend
alembic upgrade head
```

---

## How to Start the Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API Documentation (Swagger UI): `http://127.0.0.1:8000/docs`

---

## How to Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Application URL: `http://localhost:5173`

---

## Default Credentials

| Role | Username / Identifier | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `Admin@Hawlwadaag2026` | Full Administrative Portal |
| **Teacher** | `teacher_math` / `TCH-1001` | `Teacher@Hawlwadaag2026` | Teacher Portal & Assigned Classes |
| **Student** | `std_farhan` / `ADM-2026-001` | `Student@Hawlwadaag2026` | Student Portal (Self Data Only) |

---

## Running Automated Tests

```bash
cd backend
python -m pytest tests/ -v
python tests/verify_e2e_integration.py
```
