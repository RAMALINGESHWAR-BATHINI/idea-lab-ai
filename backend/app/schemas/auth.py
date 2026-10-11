"""Authentication schemas: registration, login, tokens, user projections, password reset."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import RoleName

_PASSWORD_MAX_BYTES = 72


class RegisterRequest(BaseModel):
    """Payload for ``POST /api/auth/register``."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    invitation_code: str | None = None

    @field_validator("password")
    @classmethod
    def _password_byte_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > _PASSWORD_MAX_BYTES:
            raise ValueError(
                f"Password must be at most {_PASSWORD_MAX_BYTES} bytes (bcrypt limit)"
            )
        return value

    @field_validator("full_name")
    @classmethod
    def _strip_full_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Full name must not be blank")
        return value


class LoginRequest(BaseModel):
    """Payload for ``POST /api/auth/login``."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    """Payload for ``POST /api/auth/refresh``."""

    refresh_token: str = Field(min_length=1)


class TokenResponse(BaseModel):
    """Issued token pair plus the access-token lifetime in seconds."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserRead(BaseModel):
    """Public projection of a user (never exposes password hashes)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str | None = None
    role_id: uuid.UUID | None = None
    is_superuser: bool
    is_active: bool
    is_email_verified: bool
    last_login_at: datetime | None
    created_at: datetime
    person_ref: str | None = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def _password_byte_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > _PASSWORD_MAX_BYTES:
            raise ValueError(
                f"Password must be at most {_PASSWORD_MAX_BYTES} bytes (bcrypt limit)"
            )
        return value