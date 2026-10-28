from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_active_admin
from app.models.user import User
from app.services.admin_service import AdminService
from app.repositories.audit_repo import AuditLogRepository
from app.schemas.admin import (
    DashboardOverviewResponse,
    SystemHealthResponse,
    AuditLogResponse,
)

router = APIRouter(prefix="/admin", tags=["Admin Dashboard & System Operations"])


@router.get(
    "/dashboard",
    response_model=DashboardOverviewResponse,
    summary="Get real administrative overview data and modules roadmap"
)
def get_dashboard(
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Retrieve system overview telemetry, session counts, and module statuses."""
    service = AdminService(db)
    return service.get_dashboard_overview(current_admin)


@router.get(
    "/health",
    response_model=SystemHealthResponse,
    summary="Check database and system health"
)
def get_health(
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    return service.get_system_health()


@router.get(
    "/audit-logs",
    response_model=List[AuditLogResponse],
    summary="Get recent system audit logs"
)
def get_audit_logs(
    limit: int = 20,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    audit_repo = AuditLogRepository(db)
    return audit_repo.get_recent_logs(limit=min(limit, 100))
