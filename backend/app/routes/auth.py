"""Authentication routes: register, login, refresh, current user.

Security properties:
* Registration honours ``ALLOW_REGISTRATION``.
* Login responses never reveal whether an email exists (uniform message and
  constant-time-ish verification via a dummy bcrypt hash).
* Every auth event is written to the audit log (best-effort).
* All endpoints are rate limited per-IP with a stricter auth-specific budget.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from functools import lru_cache

import jwt
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import record_audit
from app.core.config import settings
from app.core.deps import get_current_user
from app.core.errors import (
    AuthenticationError,
    ConflictError,
    PermissionDeniedError,
)
from app.core.rate_limit import limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.bootstrap import ensure_default_roles
from app.db.session import get_session
from app.models.auth import User
from app.models.enums import RoleName
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserRead,
)

router = APIRouter(tags=["auth"])


# ---- helpers ---------------------------------------------------------------


@lru_cache(maxsize=1)
def _dummy_password_hash() -> str:
    """Bcrypt hash used to equalise timing when an email is unknown."""
    return hash_password("timing-equalisation-placeholder")


def _normalise_email(email: str) -> str:
    return email.strip().lower()


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _user_agent(request: Request) -> str | None:
    return request.headers.get("user-agent")


def _issue_tokens(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
        expires_in=settings.access_token_expire_minutes * 60,
    )


def _user_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.name if user.role else None,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
    )


# ---- endpoints -------------------------------------------------------------


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.rate_limit_auth)
async def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    """Create a new account (assigned the default ``student`` role) and sign in."""
    if not settings.allow_registration:
        raise PermissionDeniedError("Registration is disabled on this instance")

    email = _normalise_email(payload.email)

    existing = await session.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise ConflictError("An account with this email already exists")

    roles = await ensure_default_roles(session)
    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=roles[RoleName.STUDENT.value],
        is_active=True,
        is_superuser=False,
    )
    session.add(user)
    try:
        await session.flush()
    except IntegrityError as exc:
        # Unique-email race with a concurrent registration.
        await session.rollback()
        raise ConflictError("An account with this email already exists") from exc

    await record_audit(
        session,
        action="auth.register",
        user_id=user.id,
        actor=email,
        resource="users",
        ip_address=_client_ip(request),
        user_agent=_user_agent(request),
        detail={"role": RoleName.STUDENT.value},
    )
    await session.commit()
    return _issue_tokens(user)



@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_auth)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    """Verify credentials and issue an access/refresh token pair."""
    email = _normalise_email(payload.email)
    user = await session.scalar(select(User).where(User.email == email))

    if user is None:
        # Equalise timing against accounts that do exist.
        verify_password(payload.password, _dummy_password_hash())
        await record_audit(
            session,
            action="auth.login",
            actor=email,
            status="failure",
            is_error=True,
            error_message="unknown email",
            ip_address=_client_ip(request),
            user_agent=_user_agent(request),
        )
        await session.commit()
        raise AuthenticationError("Invalid email or password")

    if not verify_password(payload.password, user.hashed_password):
        await record_audit(
            session,
            action="auth.login",
            user_id=user.id,
            actor=email,
            status="failure",
            is_error=True,
            error_message="bad password",
            ip_address=_client_ip(request),
            user_agent=_user_agent(request),
        )
        await session.commit()
        raise AuthenticationError("Invalid email or password")

    if not user.is_active:
        await record_audit(
            session,
            action="auth.login",
            user_id=user.id,
            actor=email,
            status="failure",
            is_error=True,
            error_message="account disabled",
            ip_address=_client_ip(request),
            user_agent=_user_agent(request),
        )
        await session.commit()
        raise AuthenticationError("Account is disabled")

    user.last_login_at = datetime.now(timezone.utc)
    await record_audit(
        session,
        action="auth.login",
        user_id=user.id,
        actor=email,
        ip_address=_client_ip(request),
        user_agent=_user_agent(request),
    )
    await session.commit()
    return _issue_tokens(user)



@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_auth)
async def refresh(
    payload: RefreshRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    """Exchange a valid refresh token for a fresh token pair."""
    try:
        data = decode_token(payload.refresh_token)
    except jwt.PyJWTError as exc:
        raise AuthenticationError("Invalid or expired refresh token") from exc

    if data.get("type") != "refresh":
        raise AuthenticationError("Refresh token required")

    try:
        user_id = uuid.UUID(str(data.get("sub")))
    except (ValueError, TypeError) as exc:
        raise AuthenticationError("Invalid token subject") from exc

    user = await session.scalar(select(User).where(User.id == user_id))
    if user is None or not user.is_active:
        raise AuthenticationError("Account is disabled or no longer exists")

    await record_audit(
        session,
        action="auth.refresh",
        user_id=user.id,
        actor=user.email,
        ip_address=_client_ip(request),
        user_agent=_user_agent(request),
    )
    await session.commit()
    return _issue_tokens(user)


@router.get("/me", response_model=UserRead)
async def current_user(user: User = Depends(get_current_user)) -> UserRead:
    """Return the profile of the authenticated user."""
    return _user_read(user)
