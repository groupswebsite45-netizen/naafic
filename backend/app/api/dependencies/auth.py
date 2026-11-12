from typing import Optional
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.core.database import get_db
from app.models.user import User
from app.repositories.user_repo import UserRepository

# HTTPBearer security scheme
security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Validate JWT access token and return the authenticated User object."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type for authorization.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(int(user_id))

    # Only fall back to central DB if the token is explicitly for a Super Admin / central user
    if not user:
        is_super = bool(payload.get("is_superuser")) or any(
            str(r).upper() in ["SUPER_ADMIN", "SUPERADMIN"] for r in (payload.get("roles") or [])
        )
        if is_super or not payload.get("database_name"):
            try:
                from app.core.tenant_context import get_central_sessionmaker
                central_session = get_central_sessionmaker()()
                try:
                    user = UserRepository(central_session).get_by_id(int(user_id))
                finally:
                    central_session.close()
            except Exception:
                user = None

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token does not exist in this institution.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive.",
        )

    return user


def get_current_super_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Enforce that the authenticated user possesses the SUPER_ADMIN role or is_superuser."""
    if not current_user.is_superuser and not current_user.has_role("SUPER_ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Administrator privileges required to access Somroyal platform resources."
        )
    return current_user


def get_current_active_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Enforce that the authenticated user possesses the ADMIN role."""
    if not current_user.has_role("ADMIN") and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required to access this resource."
        )
    return current_user


def get_current_active_teacher(
    current_user: User = Depends(get_current_user)
) -> User:
    """Enforce that the authenticated user possesses the TEACHER role."""
    if not current_user.has_role("TEACHER") and not current_user.has_role("ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Faculty / Teacher privileges required to access this resource."
        )
    return current_user


def get_current_active_student(
    current_user: User = Depends(get_current_user)
) -> User:
    """Enforce that the authenticated user possesses the STUDENT role."""
    roles = [r.upper() for r in current_user.role_names]
    if "STUDENT" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student portal privileges required to access this resource."
        )
    return current_user


def get_current_staff_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Enforce that the authenticated user possesses either ADMIN or TEACHER role."""
    roles = [r.upper() for r in current_user.role_names]
    if "ADMIN" not in roles and "TEACHER" not in roles and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative or faculty staff privileges required to access this resource."
        )
    return current_user


def get_current_user_for_media(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Validate JWT access token from Authorization header or ?token= query parameter.
    Used for media/photo endpoints so standard browser img/video tags can authenticate.
    """
    raw_token = credentials.credentials if credentials else token
    if not raw_token:
        return None

    payload = decode_token(raw_token)
    if not payload or payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(int(user_id))
    if not user:
        try:
            from app.core.tenant_context import get_central_sessionmaker
            central_session = get_central_sessionmaker()()
            try:
                user = UserRepository(central_session).get_by_id(int(user_id))
            finally:
                central_session.close()
        except Exception:
            user = None

    if not user or not user.is_active:
        return None

    return user
