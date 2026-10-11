"""Admin schemas: user/role management, audit logs, invitations, device tokens."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import RoleName


class UserRead(BaseModel):
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


class UserUpdate(BaseModel):
    full_name: str | None = None
    role_id: uuid.UUID | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_email_verified: bool | None = None


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    is_system: bool
    permissions: list[str]


class PermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None


class RoleAssignPermissions(BaseModel):
    permission_names: list[str]


class InvitationCreate(BaseModel):
    email: EmailStr | None = None
    role_name: str | None = None
    permission_names: list[str] | None = None
    scope: str | None = None
    expires_at: datetime | None = None
    max_uses: int = Field(default=1, ge=1, le=100)


class InvitationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str | None
    role_name: str | None
    scope: str | None
    status: str
    expires_at: datetime | None
    used_at: datetime | None
    used_count: int
    max_uses: int
    created_at: datetime


class AccessGrantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    grant_type: str
    scope: str
    permissions: list | None
    actor: str
    approver_id: uuid.UUID | None
    status: str
    expires_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime


class DeviceTokenCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    permissions: list[str] | None = None
    access_level: str = "public"
    expires_at: datetime | None = None
    note: str | None = None


class DeviceTokenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    permissions: list | None
    access_level: str
    is_active: bool
    last_seen_at: datetime | None
    expires_at: datetime | None
    note: str | None
    created_at: datetime


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID | None
    actor: str | None
    action: str
    resource: str | None
    status: str
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
    is_error: bool
    error_message: str | None


class SettingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    key: str
    value: str | None
    description: str | None
    is_public: bool
    created_at: datetime


class SettingUpdate(BaseModel):
    value: str
