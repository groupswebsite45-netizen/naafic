from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_system: bool = False


class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
