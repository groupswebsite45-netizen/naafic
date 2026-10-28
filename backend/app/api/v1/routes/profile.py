from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.schemas.user import UserResponse, UserProfileUpdate
from app.schemas.auth import PasswordChangeRequest

router = APIRouter(prefix="/profile", tags=["User Profile"])


@router.get(
    "",
    response_model=UserResponse,
    summary="Get profile details of the currently authenticated user"
)
def get_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.put(
    "",
    response_model=UserResponse,
    summary="Update profile details of the currently authenticated user"
)
def update_profile(
    payload: UserProfileUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    service = UserService(db)
    return service.update_profile(
        user=current_user,
        data=payload,
        ip_address=client_ip
    )


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change user password with current password verification"
)
def change_password(
    payload: PasswordChangeRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    auth_service = AuthService(db)
    auth_service.change_password(
        user=current_user,
        data=payload,
        ip_address=client_ip
    )
    return {"message": "Password changed successfully. Please log in with your new password."}
