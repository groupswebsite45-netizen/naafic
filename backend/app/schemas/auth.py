from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    """Login request payload supporting email or username."""
    identifier: str = Field(..., description="Email or Username", min_length=3)
    password: str = Field(..., description="User password", min_length=1)
    remember_me: Optional[bool] = False


class InstitutionLoginInfo(BaseModel):
    id: int
    code: str
    name: str
    type: Optional[str] = "School"
    logo_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    database_name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
    institution: Optional[InstitutionLoginInfo] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


class CurrentUserResponse(BaseModel):
    user: UserResponse
    permissions: List[str] = []
    institution: Optional[InstitutionLoginInfo] = None
