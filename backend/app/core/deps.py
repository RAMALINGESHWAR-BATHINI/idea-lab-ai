"""Shared FastAPI dependencies."""
from __future__ import annotations

import uuid

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AuthenticationError
from app.core.security import decode_token
from app.db.session import get_session
from app.models.auth import User

# auto_error=False so missing credentials produce OUR 401 envelope, not
# FastAPI's default "Not authenticated" body.
_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Resolve the authenticated user from ``Authorization: Bearer <access token>``.

    Raises ``AuthenticationError`` (401) for missing/invalid/expired tokens,
    wrong token types, unknown users and disabled accounts.
    """
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Authentication credentials were not provided")

    try:
        payload = decode_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise AuthenticationError("Invalid or expired token") from exc

    if payload.get("type") != "access":
        raise AuthenticationError("Access token required")

    subject = payload.get("sub")
    try:
        user_id = uuid.UUID(str(subject))
    except (ValueError, TypeError, AttributeError) as exc:
        raise AuthenticationError("Invalid token subject") from exc

    user = await session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise AuthenticationError("User no longer exists")
    if not user.is_active:
        raise AuthenticationError("Account is disabled")
    return user