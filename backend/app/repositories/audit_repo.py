from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.repositories.base_repo import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """AuditLog repository for recording and fetching system audit events."""

    def __init__(self, db: Session):
        super().__init__(AuditLog, db)

    def log_event(
        self,
        action: str,
        status: str = "SUCCESS",
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        return self.create(audit_entry)

    def get_recent_logs(self, limit: int = 10) -> List[AuditLog]:
        return self.db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
