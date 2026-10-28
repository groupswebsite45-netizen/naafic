from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from app.schemas.role import RoleResponse


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=200)
    phone_number: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role_names: List[str] = Field(default=["STUDENT"])


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    phone_number: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_superuser: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    roles: List[RoleResponse] = []

    model_config = ConfigDict(from_attributes=True)
