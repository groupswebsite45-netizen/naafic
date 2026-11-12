import time
from datetime import datetime, timezone, date
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.core.config import settings
from app.models.user import User
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.exam import Exam
from app.models.timetable import Timetable
from app.models.fee import StudentFee, FeePayment
from app.repositories.session_repo import SessionRepository
from app.repositories.audit_repo import AuditLogRepository
from app.repositories.fee_repo import FeeRepository
from app.schemas.admin import (
    DashboardOverviewResponse,
    SystemHealthResponse,
    ModuleStatus,
)

STARTUP_TIME = time.time()


class AdminService:
    """Service handling Admin Dashboard, system monitoring, and real school metrics."""

    def __init__(self, db: Session):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.audit_repo = AuditLogRepository(db)
        self.fee_repo = FeeRepository(db)

    def get_system_health(self) -> SystemHealthResponse:
        db_connected = False
        try:
            self.db.execute(text("SELECT 1"))
            db_connected = True
        except Exception:
            db_connected = False

        return SystemHealthResponse(
            status="healthy" if db_connected else "degraded",
            database_connected=db_connected,
            database_name="sms",
            server_time=datetime.now(timezone.utc),
            app_version="1.0.0-production",
            environment=settings.APP_ENV
        )

    def get_dashboard_overview(self, current_admin: User) -> Dict[str, Any]:
        """Fetch real system telemetry, session counts, and live school metrics from PostgreSQL."""
        active_sessions = self.session_repo.count_active_sessions()
        uptime_seconds = time.time() - STARTUP_TIME

        # Real PostgreSQL metrics
        total_students = self.db.query(Student).count()
        active_students = self.db.query(Student).filter(Student.status == "ACTIVE").count()

        total_teachers = self.db.query(Teacher).count()
        active_teachers = self.db.query(Teacher).filter(Teacher.status == "ACTIVE").count()

        total_classes = self.db.query(SchoolClass).count()
        total_subjects = self.db.query(Subject).count()

        # Timetable for today
        today_name = datetime.now().strftime("%A")
        today_timetable_count = self.db.query(Timetable).filter(
            Timetable.day_of_week == today_name,
            Timetable.status == "ACTIVE"
        ).count()

        # Upcoming/active exams
        upcoming_exams_count = self.db.query(Exam).filter(
            Exam.status.in_(["SCHEDULED", "ONGOING"])
        ).count()

        # Financial summary from PostgreSQL
        financials = self.fee_repo.get_financial_summary()

        # Modules catalog with installed status
        modules: List[ModuleStatus] = [
            ModuleStatus(
                id="auth_admin",
                name="System & Admin Authentication",
                description="Secure RBAC, JWT tokens, and administrative session management.",
                status="AVAILABLE",
                is_installed=True,
                badge_color="success",
                route_path="/admin"
            ),
            ModuleStatus(
                id="classes",
                name="Classes & Sections",
                description="Manage primary and secondary grade classes, sections, and capacities.",
                status="AVAILABLE",
                is_installed=True,
                badge_color="success",
                route_path="/admin/classes"
            ),
            ModuleStatus(
                id="subjects",
                name="Academic Subjects",
                description="Curriculum subjects, departmental groupings, and academic codes.",
                status="AVAILABLE",
                is_installed=True,
                badge_color="success",
                route_path="/admin/subjects"
            ),
            ModuleStatus(
                id="teachers",
                name="Teacher Management",
                description="Faculty records, portal accounts, and class-subject assignments.",
                status="AVAILABLE",
                is_installed=True,
                badge_color="success",
                route_path="/admin/teachers"
            ),
            ModuleStatus(
                id="students",
                name="Student Management",
                description="Student admissions, bio-data, class enrollments, and portal accounts.",
                status="AVAILABLE",
                is_installed=True,
                badge_color="success",
                route_path="/admin/students"
            ),
            ModuleStatus(
                id="timetable",
                name="Class Timetable",
                description="Weekly class schedule management with backend conflict prevention.",
                status="AVAILABLE",
                is_installed=True,
                badge_color="success",
                route_path="/admin/timetable"
            ),
            ModuleStatus(
                id="fees",
                name="Fee Management & Billing",
                description="Fee structures, student invoices, and payment receipts.",
                status="AVAILABLE",
                is_installed=True,
                badge_color="success",
                route_path="/admin/fees"
            ),
            ModuleStatus(
                id="exams",
                name="Exams & Grading",
                description="Examinations, assessments, marks entry, and report cards.",
                status="AVAILABLE",
                is_installed=True,
                badge_color="success",
                route_path="/admin/exams"
            ),
        ]

        recent_logs = self.audit_repo.get_recent_logs(limit=6)
        recent_activity = [
            {
                "id": log.id,
                "action": log.action,
                "status": log.status,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat(),
                "details": log.details
            }
            for log in recent_logs
        ]

        # Fetch school branding settings from this tenant's system_settings
        from app.models.system_setting import SystemSetting
        settings_rows = self.db.query(SystemSetting).all()
        settings_map = {s.key: s.value for s in settings_rows}

        current_db_name = "sms"
        if self.db and hasattr(self.db, "bind") and self.db.bind:
            current_db_name = self.db.bind.url.database or "sms"

        school_info = {
            "name": settings_map.get("school_name", "Educational Institution"),
            "code": settings_map.get("school_code", "EMS-001"),
            "type": settings_map.get("school_type", "School"),
            "logo_url": settings_map.get("logo_url") or None,
            "academic_year": settings_map.get("active_academic_year", "2026/2027"),
            "city": settings_map.get("city", "Mogadishu"),
            "email": settings_map.get("contact_email", ""),
            "phone": settings_map.get("contact_phone", ""),
        }

        return {
            "system_status": "ONLINE",
            "database_status": "CONNECTED",
            "database_name": current_db_name,
            "active_sessions_count": active_sessions,
            "system_uptime_seconds": uptime_seconds,
            "current_admin": current_admin,
            "modules": modules,
            "recent_activity": recent_activity,
            "school": school_info,
            # Real metrics
            "metrics": {
                "total_students": total_students,
                "active_students": active_students,
                "total_teachers": total_teachers,
                "active_teachers": active_teachers,
                "total_classes": total_classes,
                "total_subjects": total_subjects,
                "today_timetable_count": today_timetable_count,
                "upcoming_exams_count": upcoming_exams_count,
                "total_fees_billed": financials["total_billed"],
                "total_fees_collected": financials["total_collected"],
                "total_fees_outstanding": financials["total_outstanding"],
            }
        }
