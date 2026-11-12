from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User
from app.models.session import SessionModel
from app.repositories.user_repo import UserRepository
from app.repositories.session_repo import SessionRepository
from app.repositories.audit_repo import AuditLogRepository
from app.schemas.auth import LoginRequest, TokenResponse, PasswordChangeRequest


class AuthService:
    """Service handling all authentication and authorization logic."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def authenticate(
        self,
        login_data: LoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TokenResponse:
        """Authenticate user by identifier (email/username) and password with multi-tenant auto-discovery."""
        matched_institution = None
        user = self.user_repo.get_by_identifier(login_data.identifier)
        is_verified = False

        if user and verify_password(login_data.password, user.hashed_password):
            is_verified = True
            try:
                from app.core.tenant_context import get_central_sessionmaker, get_default_database_name
                from app.models.institution import Institution
                from sqlalchemy import or_
                default_db = get_default_database_name()
                cur_db = default_db
                if self.db and hasattr(self.db, "bind") and self.db.bind:
                    cur_db = self.db.bind.url.database or default_db
                with get_central_sessionmaker()() as cs:
                    matched_institution = cs.query(Institution).filter(
                        or_(
                            Institution.database_name == cur_db,
                            (Institution.id == 1 if cur_db in ["sms", default_db] else False)
                        )
                    ).first()
            except Exception:
                pass

        # If not verified in current routed DB, perform Smart Cross-Tenant Discovery:
        if not is_verified:
            try:
                from app.core.tenant_context import get_central_sessionmaker, get_tenant_sessionmaker, get_default_database_name
                from app.models.institution import Institution
                from sqlalchemy import or_, func

                clean_identifier = login_data.identifier.strip().lower()
                default_db = get_default_database_name()

                with get_central_sessionmaker()() as central_session:
                    # 1. First check if this is Super Admin in central database
                    central_user = UserRepository(central_session).get_by_identifier(login_data.identifier)
                    if central_user and (central_user.is_superuser or any(r.name == "SUPER_ADMIN" for r in central_user.roles)):
                        if verify_password(login_data.password, central_user.hashed_password):
                            self.db = central_session
                            self.user_repo = UserRepository(central_session)
                            self.session_repo = SessionRepository(central_session)
                            self.audit_repo = AuditLogRepository(central_session)
                            user = central_user
                            is_verified = True
                            matched_institution = None

                    # 2. Check candidate institutions where identifier matches admin_username, admin_email, or code
                    if not is_verified:
                        candidate_insts = central_session.query(Institution).filter(
                            Institution.status == "ACTIVE",
                            or_(
                                func.lower(func.trim(Institution.admin_username)) == clean_identifier,
                                func.lower(func.trim(Institution.admin_email)) == clean_identifier,
                                func.lower(func.trim(Institution.code)) == clean_identifier,
                            )
                        ).all()

                        for inst in candidate_insts:
                            target_db = inst.database_name
                            if not target_db or target_db.lower() == "sms" or inst.id == 1:
                                target_db = default_db
                            try:
                                tenant_session = get_tenant_sessionmaker(target_db)()
                                try:
                                    t_user = UserRepository(tenant_session).get_by_identifier(login_data.identifier)
                                    if t_user and verify_password(login_data.password, t_user.hashed_password):
                                        self.db = tenant_session
                                        self.user_repo = UserRepository(tenant_session)
                                        self.session_repo = SessionRepository(tenant_session)
                                        self.audit_repo = AuditLogRepository(tenant_session)
                                        user = t_user
                                        is_verified = True
                                        matched_institution = inst
                                        break
                                finally:
                                    if not is_verified:
                                        tenant_session.close()
                            except Exception:
                                pass

                    # 3. If still not verified, check all other active tenant databases (teachers, students, staff)
                    if not is_verified:
                        all_insts = central_session.query(Institution).filter(Institution.status == "ACTIVE").all()
                        for inst in all_insts:
                            target_db = inst.database_name
                            if not target_db or target_db.lower() == "sms" or inst.id == 1:
                                target_db = default_db
                            try:
                                tenant_session = get_tenant_sessionmaker(target_db)()
                                try:
                                    t_user = UserRepository(tenant_session).get_by_identifier(login_data.identifier)
                                    if t_user and verify_password(login_data.password, t_user.hashed_password):
                                        self.db = tenant_session
                                        self.user_repo = UserRepository(tenant_session)
                                        self.session_repo = SessionRepository(tenant_session)
                                        self.audit_repo = AuditLogRepository(tenant_session)
                                        user = t_user
                                        is_verified = True
                                        matched_institution = inst
                                        break
                                finally:
                                    if not is_verified:
                                        tenant_session.close()
                            except Exception:
                                pass
            except Exception as e:
                print(f"Error during cross-tenant user discovery: {e}")

        # Constant-time comparison simulation / safe non-revealing error
        if not user or not is_verified:
            self.audit_repo.log_event(
                action="LOGIN_FAILED",
                status="FAILURE",
                user_id=user.id if user else None,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"identifier_used": login_data.identifier}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            self.audit_repo.log_event(
                action="LOGIN_DEACTIVATED",
                status="FAILURE",
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"reason": "Account is inactive"}
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive. Please contact the administrator."
            )

        # Update last login timestamp
        self.user_repo.update_last_login(user.id)

        # Generate tokens
        role_names = [r.name for r in user.roles]
        from app.core.tenant_context import get_default_database_name
        default_db = get_default_database_name()

        if matched_institution and matched_institution.database_name:
            db_name = matched_institution.database_name
        else:
            db_name = default_db
            try:
                if self.db and hasattr(self.db, "bind") and self.db.bind:
                    db_name = self.db.bind.url.database or default_db
            except Exception:
                db_name = default_db

        token_claims = {
            "email": user.email,
            "username": user.username,
            "roles": role_names,
            "is_superuser": user.is_superuser,
            "database_name": db_name,
            "institution_code": matched_institution.code if matched_institution else None,
            "institution_id": matched_institution.id if matched_institution else None,
            "institution_name": matched_institution.name if matched_institution else None,
            "institution_logo_url": matched_institution.logo_url if matched_institution else None,
        }

        access_token_expires = timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES if not login_data.remember_me else 60 * 24
        )
        access_token = create_access_token(
            subject=user.id,
            claims=token_claims,
            expires_delta=access_token_expires
        )

        refresh_token_expires = timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS if not login_data.remember_me else 30
        )
        refresh_token = create_refresh_token(
            subject=user.id,
            expires_delta=refresh_token_expires
        )

        # Store session in database
        expires_at = datetime.now(timezone.utc) + refresh_token_expires
        session_entry = SessionModel(
            user_id=user.id,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            is_revoked=False
        )
        self.session_repo.create(session_entry)

        # Audit successful login
        self.audit_repo.log_event(
            action="LOGIN_SUCCESS",
            status="SUCCESS",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"roles": role_names}
        )

        inst_info = None
        if matched_institution:
            inst_info = {
                "id": matched_institution.id,
                "code": matched_institution.code,
                "name": matched_institution.name,
                "type": matched_institution.type or "School",
                "logo_url": matched_institution.logo_url,
                "email": matched_institution.email,
                "phone": matched_institution.phone,
                "city": matched_institution.city,
                "address": matched_institution.address,
                "database_name": matched_institution.database_name or db_name,
            }

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds()),
            user=user,
            institution=inst_info
        )

    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Issue new access token from valid refresh token."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token."
            )

        session = self.session_repo.get_by_refresh_token(refresh_token)
        if not session or not session.is_valid():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has expired or was revoked."
            )

        user = self.user_repo.get_by_id(session.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account no longer active."
            )

        role_names = [r.name for r in user.roles]
        default_db = "hawlwadaag_school_db"
        try:
            from app.core.tenant_context import get_default_database_name
            default_db = get_default_database_name()
        except Exception:
            pass
        db_name = default_db
        try:
            if self.db and hasattr(self.db, "bind") and self.db.bind:
                db_name = self.db.bind.url.database or default_db
        except Exception:
            db_name = default_db

        token_claims = {
            "email": user.email,
            "username": user.username,
            "roles": role_names,
            "is_superuser": user.is_superuser,
            "database_name": db_name,
        }

        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            subject=user.id,
            claims=token_claims,
            expires_delta=access_token_expires
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds()),
            user=user
        )

    def logout(self, user_id: int, refresh_token: Optional[str] = None) -> None:
        """Revoke active session on logout."""
        if refresh_token:
            self.session_repo.revoke_token(refresh_token)
        else:
            self.session_repo.revoke_all_user_sessions(user_id)

        self.audit_repo.log_event(
            action="LOGOUT",
            status="SUCCESS",
            user_id=user_id,
            details={"message": "Logged out successfully"}
        )

    def change_password(
        self,
        user: User,
        data: PasswordChangeRequest,
        ip_address: Optional[str] = None
    ) -> None:
        """Verify current password and set new password securely."""
        if not verify_password(data.current_password, user.hashed_password):
            self.audit_repo.log_event(
                action="PASSWORD_CHANGE_FAILED",
                status="FAILURE",
                user_id=user.id,
                ip_address=ip_address,
                details={"reason": "Incorrect current password"}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password verification failed."
            )

        if data.current_password == data.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password cannot be identical to current password."
            )

        user.hashed_password = get_password_hash(data.new_password)
        self.user_repo.update(user)

        # Invalidate existing sessions for security
        self.session_repo.revoke_all_user_sessions(user.id)

        self.audit_repo.log_event(
            action="PASSWORD_CHANGED",
            status="SUCCESS",
            user_id=user.id,
            ip_address=ip_address,
            details={"message": "Password updated successfully"}
        )
