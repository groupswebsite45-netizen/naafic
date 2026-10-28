from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.role import Role
from app.repositories.base_repo import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Role repository for database operations."""

    def __init__(self, db: Session):
        super().__init__(Role, db)

    def get_by_name(self, name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == name.upper().strip()).first()

    def get_or_create(self, name: str, description: Optional[str] = None, is_system: bool = False) -> Role:
        role = self.get_by_name(name)
        if not role:
            role = Role(
                name=name.upper().strip(),
                description=description,
                is_system=is_system
            )
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
        return role
