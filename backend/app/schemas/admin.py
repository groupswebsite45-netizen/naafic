from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserResponse


class SystemHealthResponse(BaseModel):
    status: str
    database_connected: bool
    database_name: str
    server_time: datetime
    app_version: str
    environment: str


class ModuleStatus(BaseModel):
    id: str
    name: str
    description: str
    status: str  # "AVAILABLE", "PLANNED", "DEVELOPMENT"
    is_installed: bool
    badge_color: str
    route_path: Optional[str] = None


class DashboardOverviewResponse(BaseModel):
    system_status: str
    database_status: str
    database_name: str
    active_sessions_count: int
    system_uptime_seconds: float
    current_admin: UserResponse
    modules: List[ModuleStatus]
    recent_activity: List[Dict[str, Any]] = []
    metrics: Optional[Dict[str, Any]] = None


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    status: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    details: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
