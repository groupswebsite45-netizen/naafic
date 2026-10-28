from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SystemSettingBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    is_public: bool = False


class SystemSettingResponse(SystemSettingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SystemSettingUpdate(BaseModel):
    value: str
    description: Optional[str] = None
    is_public: Optional[bool] = None
