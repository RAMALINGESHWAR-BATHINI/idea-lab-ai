"""Password hashing and JWT token utilities."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import settings

# bcrypt truncates input beyond 72 bytes; guard against silent truncation.
_BCRYPT_MAX_BYTES = 72


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    if not password:
        raise ValueError("Password must not be empty")
    raw = password.encode("utf-8")
    if len(raw) > _BCRYPT_MAX_BYTES:
        raise ValueError("Password is too long (max 72 bytes)")
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    if not password or not hashed:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def _create_token(
    subject: str,
    token_type: str,
    expires_minutes: int,
    extra: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
        "jti": str(uuid.uuid4()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    """Create a short-lived access token for a user id."""
    return _create_token(
        subject, "access", settings.access_token_expire_minutes, extra
    )


def create_refresh_token(subject: str) -> str:
    """Create a long-lived refresh token for a user id."""
    return _create_token(subject, "refresh", settings.refresh_token_expire_minutes)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT.

    Raises ``jwt.PyJWTError`` subclasses on any validation failure.
    """
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
    )
