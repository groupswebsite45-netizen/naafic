from typing import Optional
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    CurrentUserResponse,
)
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and obtain JWT tokens"
)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Authenticate user with identifier (email/username) and password."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    service = AuthService(db)
    return service.authenticate(
        login_data=payload,
        ip_address=client_ip,
        user_agent=user_agent
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Obtain a new access token using a valid refresh token"
)
def refresh_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    service = AuthService(db)
    return service.refresh_access_token(payload.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user and invalidate active session"
)
def logout(
    payload: Optional[RefreshTokenRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AuthService(db)
    token_to_revoke = payload.refresh_token if payload else None
    service.logout(user_id=current_user.id, refresh_token=token_to_revoke)
    return {"message": "Successfully logged out."}


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    summary="Get currently authenticated user details"
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    role_names = [r.name for r in current_user.roles]
    permissions = []
    if "ADMIN" in role_names or current_user.is_superuser:
        permissions.append("admin:access")
        permissions.append("admin:settings")

    return CurrentUserResponse(
        user=current_user,
        permissions=permissions
    )
