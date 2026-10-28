# Backend API - Hawlwadaag School Management System

FastAPI RESTful Backend providing Authentication, RBAC, Admin Services, and PostgreSQL Database connectivity for **Hawlwadaag Primary and Secondary School**.

## Architecture & Technologies

- **Framework**: FastAPI (Python 3.10+)
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL (`hawlwadaag_school_db`)
- **Schema Migrations**: Alembic
- **Validation**: Pydantic v2
- **Authentication**: JWT (JSON Web Tokens) with PyJWT & Bcrypt password hashing
- **Server**: Uvicorn ASGI

## Folder Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── dependencies/    # Auth (get_current_user, get_current_active_admin) & DB session
│   │   └── v1/
│   │       ├── routes/      # Auth, Admin, Profile, System endpoints
│   │       └── api.py       # API v1 Router aggregator
│   ├── core/
│   │   ├── config.py        # Environment settings (Pydantic Settings)
│   │   ├── database.py      # SQLAlchemy Engine & SessionLocal
│   │   └── security.py      # Bcrypt & JWT token utilities
│   ├── middleware/          # CORS & Centralized Error Handlers
│   ├── models/              # SQLAlchemy Database Models (User, Role, UserRole, Session, AuditLog, SystemSetting)
│   ├── repositories/        # Database Query Abstractions (UserRepo, RoleRepo, SessionRepo, etc.)
│   ├── schemas/             # Pydantic Request/Response Models
│   ├── services/            # Core Business Logic (AuthService, UserService, AdminService)
│   ├── utils/               # Structured Logger & Utilities
│   └── main.py              # Lean FastAPI application entrypoint
├── alembic/                 # Alembic migration scripts and environment
├── scripts/                 # Database seed utility (seed.py)
├── tests/                   # Pytest test suite
├── .env.example             # Example environment variables
├── requirements.txt         # Python package dependencies
└── README.md
```

## Setup & Running

### 1. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure `DATABASE_URL` matches your local PostgreSQL instance:
```env
DATABASE_URL=postgresql+psycopg2://postgres:123@localhost:5432/hawlwadaag_school_db
```

### 2. Apply Database Migrations
```bash
python -m alembic upgrade head
```

### 3. Seed Initial Roles, Settings & Admin User
```bash
python scripts/seed.py
```
Default Development Admin:
- **Username**: `admin`
- **Email**: `admin@hawlwadaagschool.edu.so`
- **Password**: `Admin@Hawlwadaag2026`

### 4. Run Development Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```
- API Docs: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/health`

### 5. Run Automated Tests
```bash
python -m pytest tests/ -v
```
