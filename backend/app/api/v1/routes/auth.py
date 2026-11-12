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
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    role_names = [r.name for r in current_user.roles]
    permissions = []
    if "ADMIN" in role_names or current_user.is_superuser:
        permissions.append("admin:access")
        permissions.append("admin:settings")

    # Resolve institution context
    inst_info = None
    try:
        from app.core.tenant_context import extract_tenant_context_from_request, get_central_sessionmaker, get_default_database_name
        from app.models.institution import Institution
        from app.schemas.auth import InstitutionLoginInfo
        ctx = extract_tenant_context_from_request(request)
        default_db = get_default_database_name()
        cur_db = ctx.get("db_name")
        if not cur_db and db and hasattr(db, "bind") and db.bind:
            cur_db = db.bind.url.database

        if cur_db and cur_db.lower() not in ["sms", default_db.lower()] or ctx.get("code") or ctx.get("id"):
            with get_central_sessionmaker()() as cs:
                inst = None
                if ctx.get("code"):
                    inst = cs.query(Institution).filter(Institution.code == ctx["code"]).first()
                elif ctx.get("id"):
                    inst = cs.query(Institution).filter(Institution.id == int(ctx["id"])).first()
                elif cur_db:
                    inst = cs.query(Institution).filter(Institution.database_name == cur_db).first()

                if inst:
                    inst_info = InstitutionLoginInfo(
                        id=inst.id,
                        code=inst.code,
                        name=inst.name,
                        type=inst.type or "School",
                        logo_url=inst.logo_url,
                        email=inst.email,
                        phone=inst.phone,
                        city=inst.city,
                        address=inst.address,
                        database_name=inst.database_name,
                    )
    except Exception:
        pass

    return CurrentUserResponse(
        user=current_user,
        permissions=permissions,
        institution=inst_info
    )
