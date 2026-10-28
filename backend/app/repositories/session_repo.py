from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.session import SessionModel
from app.repositories.base_repo import BaseRepository


class SessionRepository(BaseRepository[SessionModel]):
    """Session repository for refresh tokens and active user sessions."""

    def __init__(self, db: Session):
        super().__init__(SessionModel, db)

    def get_by_refresh_token(self, token: str) -> Optional[SessionModel]:
        return self.db.query(SessionModel).filter(
            SessionModel.refresh_token == token,
            SessionModel.is_revoked == False  # noqa: E712
        ).first()

    def get_active_sessions_by_user(self, user_id: int) -> List[SessionModel]:
        now = datetime.now(timezone.utc)
        return self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.is_revoked == False,  # noqa: E712
            SessionModel.expires_at > now
        ).all()

    def count_active_sessions(self) -> int:
        now = datetime.now(timezone.utc)
        return self.db.query(SessionModel).filter(
            SessionModel.is_revoked == False,  # noqa: E712
            SessionModel.expires_at > now
        ).count()

    def revoke_token(self, token: str) -> bool:
        session = self.get_by_refresh_token(token)
        if session:
            session.is_revoked = True
            self.db.commit()
            return True
        return False

    def revoke_all_user_sessions(self, user_id: int) -> int:
        sessions = self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.is_revoked == False  # noqa: E712
        ).all()
        for s in sessions:
            s.is_revoked = True
        self.db.commit()
        return len(sessions)
