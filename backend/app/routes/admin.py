"""Admin routes: user management, roles, permissions, invitations, devices."""
from __future__ import annotations

import hashlib
import secrets
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.errors import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
from app.core.security import hash_password
from app.db.session import get_session
from app.models.auth import (
    Permission,
    Role,
    User,
)
from app.models.devices import DeviceToken
from app.models.invitations import AccessGrant, Invitation
from app.models.settings import SystemSetting
from app.schemas.admin import (
    AccessGrantRead,
    AuditLogRead,
    DeviceTokenCreate,
    DeviceTokenRead,
    InvitationCreate,
    InvitationRead,
    PermissionRead,
    RoleAssignPermissions,
    RoleRead,
    SettingRead,
    SettingUpdate,
    UserRead as AdminUserRead,
    UserUpdate,
)

router = APIRouter(tags=["admin"])

CurrentUser = Depends(get_current_user)


def _require_superuser(user: User) -> None:
    if not user.is_superuser:
        raise PermissionDeniedError("Superuser access required")


def _require_permission(user: User, permission: str) -> None:
    if user.is_superuser:
        return
    if not user.has_permission(permission):
        raise PermissionDeniedError(f"Missing permission: {permission}")


# ---- Users -----------------------------------------------------------------

@router.get("/users", response_model=list[AdminUserRead])
async def list_users(
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> list[AdminUserRead]:
    _require_permission(user, "users.manage")
    result = await session.execute(select(User).order_by(User.created_at))
    users = list(result.scalars())
    return [AdminUserRead.model_validate(u) for u in users]


@router.get("/users/{user_id}", response_model=AdminUserRead)
async def get_user(
    user_id: uuid.UUID,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> AdminUserRead:
    _require_permission(user, "users.manage")
    u = await session.get(User, user_id)
    if not u:
        raise NotFoundError("User not found")
    return AdminUserRead.model_validate(u)


@router.patch("/users/{user_id}", response_model=AdminUserRead)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> AdminUserRead:
    _require_permission(user, "users.manage")
    u = await session.get(User, user_id)
    if not u:
        raise NotFoundError("User not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(u, field, value)
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return AdminUserRead.model_validate(u)


@router.post("/users/{user_id}/reset-password", status_code=status.HTTP_200_OK)
async def reset_user_password(
    user_id: uuid.UUID,
    new_password: str,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    _require_permission(user, "users.manage")
    u = await session.get(User, user_id)
    if not u:
        raise NotFoundError("User not found")
    u.hashed_password = hash_password(new_password)
    session.add(u)
    await session.commit()
    return {"status": "ok"}


# ---- Roles & Permissions ---------------------------------------------------

@router.get("/roles", response_model=list[RoleRead])
async def list_roles(
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> list[RoleRead]:
    _require_permission(user, "roles.manage")
    result = await session.execute(select(Role).order_by(Role.name))
    roles = list(result.scalars())
    return [
        RoleRead(
            id=r.id,
            name=r.name,
            description=r.description,
            is_system=r.is_system,
            permissions=[p.name for p in r.permissions],
        )
        for r in roles
    ]


@router.get("/roles/{role_id}", response_model=RoleRead)
async def get_role(
    role_id: uuid.UUID,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> RoleRead:
    _require_permission(user, "roles.manage")
    r = await session.get(Role, role_id)
    if not r:
        raise NotFoundError("Role not found")
    return RoleRead(
        id=r.id,
        name=r.name,
        description=r.description,
        is_system=r.is_system,
        permissions=[p.name for p in r.permissions],
    )


@router.post("/roles/{role_id}/permissions", response_model=RoleRead)
async def assign_permissions(
    role_id: uuid.UUID,
    payload: RoleAssignPermissions,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> RoleRead:
    _require_permission(user, "roles.manage")
    r = await session.get(Role, role_id)
    if not r:
        raise NotFoundError("Role not found")
    r.permissions.clear()
    for perm_name in payload.permission_names:
        result = await session.execute(
            select(Permission).where(Permission.name == perm_name)
        )
        perm = result.scalar_one_or_none()
        if perm is None:
            raise NotFoundError(f"Permission '{perm_name}' not found")
        r.permissions.append(perm)
    await session.commit()
    await session.refresh(r)
    return RoleRead(
        id=r.id,
        name=r.name,
        description=r.description,
        is_system=r.is_system,
        permissions=[p.name for p in r.permissions],
    )


@router.get("/permissions", response_model=list[PermissionRead])
async def list_permissions(
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> list[PermissionRead]:
    _require_permission(user, "roles.manage")
    result = await session.execute(select(Permission).order_by(Permission.name))
    perms = list(result.scalars())
    return [PermissionRead.model_validate(p) for p in perms]


# ---- Invitations -----------------------------------------------------------

def _hash_code(code: str) -> str:
    """Hash an invitation code for storage (SHA-256)."""
    return hashlib.sha256(code.encode()).hexdigest()


@router.post("/invitations", response_model=InvitationRead, status_code=status.HTTP_201_CREATED)
async def create_invitation(
    payload: InvitationCreate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> InvitationRead:
    _require_permission(user, "invitations.manage")
    code = secrets.token_urlsafe(16)[:12]

    role_id = None
    if payload.role_name:
        result = await session.execute(
            select(Role).where(Role.name == payload.role_name)
        )
        role = result.scalar_one_or_none()
        if role is None:
            raise NotFoundError(f"Role '{payload.role_name}' not found")
        role_id = role.id

    inv = Invitation(
        code_hash=_hash_code(code),
        email=payload.email,
        role_id=role_id,
        permissions=payload.permission_names,
        scope=payload.scope,
        expires_at=payload.expires_at,
        max_uses=payload.max_uses,
        created_by=user.id,
    )
    session.add(inv)
    await session.commit()
    await session.refresh(inv)
    return InvitationRead(
        id=inv.id,
        email=inv.email,
        role_name=inv.role.name if inv.role else None,
        scope=inv.scope,
        status=inv.status.value,
        expires_at=inv.expires_at,
        used_at=inv.used_at,
        used_count=inv.used_count,
        max_uses=inv.max_uses,
        created_at=inv.created_at,
    )


@router.get("/invitations", response_model=list[InvitationRead])
async def list_invitations(
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> list[InvitationRead]:
    _require_permission(user, "invitations.manage")
    result = await session.execute(select(Invitation).order_by(Invitation.created_at.desc()))
    invs = list(result.scalars())
    return [
        InvitationRead(
            id=i.id,
            email=i.email,
            role_name=i.role.name if i.role else None,
            scope=i.scope,
            status=i.status.value,
            expires_at=i.expires_at,
            used_at=i.used_at,
            used_count=i.used_count,
            max_uses=i.max_uses,
            created_at=i.created_at,
        )
        for i in invs
    ]


# ---- Access Grants ----------------------------------------------------------

@router.get("/access-grants", response_model=list[AccessGrantRead])
async def list_access_grants(
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> list[AccessGrantRead]:
    _require_permission(user, "access_grants.manage")
    result = await session.execute(select(AccessGrant).order_by(AccessGrant.created_at.desc()))
    grants = list(result.scalars())
    return [
        AccessGrantRead(
            id=g.id,
            grant_type=g.grant_type.value,
            scope=g.scope,
            permissions=g.permissions,
            actor=g.actor,
            approver_id=g.approver_id,
            status=g.status,
            expires_at=g.expires_at,
            revoked_at=g.revoked_at,
            created_at=g.created_at,
        )
        for g in grants
    ]


# ---- Device Tokens ----------------------------------------------------------

@router.post("/devices", response_model=DeviceTokenRead, status_code=status.HTTP_201_CREATED)
async def create_device_token(
    payload: DeviceTokenCreate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> DeviceTokenRead:
    _require_permission(user, "devices.register")
    raw_token = secrets.token_urlsafe(32)
    token = DeviceToken(
        name=payload.name,
        token_hash=hash_password(raw_token),
        permissions=payload.permissions,
        access_level=payload.access_level,
        expires_at=payload.expires_at,
        note=payload.note,
    )
    session.add(token)
    await session.commit()
    await session.refresh(token)
    # We don't return the raw token in the response — in production this
    # would be displayed once at creation time.
    return DeviceTokenRead(
        id=token.id,
        name=token.name,
        permissions=token.permissions,
        access_level=token.access_level,
        is_active=token.is_active,
        last_seen_at=token.last_seen_at,
        expires_at=token.expires_at,
        note=token.note,
        created_at=token.created_at,
    )


@router.get("/devices", response_model=list[DeviceTokenRead])
async def list_device_tokens(
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> list[DeviceTokenRead]:
    _require_permission(user, "devices.manage")
    result = await session.execute(select(DeviceToken).order_by(DeviceToken.created_at.desc()))
    tokens = list(result.scalars())
    return [
        DeviceTokenRead(
            id=t.id,
            name=t.name,
            permissions=t.permissions,
            access_level=t.access_level,
            is_active=t.is_active,
            last_seen_at=t.last_seen_at,
            expires_at=t.expires_at,
            note=t.note,
            created_at=t.created_at,
        )
        for t in tokens
    ]


# ---- Audit Logs -------------------------------------------------------------

@router.get("/audit-logs", response_model=list[AuditLogRead])
async def list_audit_logs(
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
    limit: int = 200,
) -> list[AuditLogRead]:
    _require_permission(user, "audit.read")
    from app.models.audit import AuditLog

    result = await session.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    )
    logs = list(result.scalars())
    return [AuditLogRead.model_validate(l) for l in logs]


# ---- System Settings --------------------------------------------------------

@router.get("/settings", response_model=list[SettingRead])
async def list_settings(
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> list[SettingRead]:
    _require_permission(user, "system.settings.manage")
    result = await session.execute(select(SystemSetting))
    settings_list = list(result.scalars())
    return [
        SettingRead(
            id=s.id,
            key=s.key,
            value=s.value,
            description=s.description,
            is_public=s.is_public,
            created_at=s.created_at,
        )
        for s in settings_list
    ]


@router.patch("/settings/{key}", response_model=SettingRead)
async def update_setting(
    key: str,
    payload: SettingUpdate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> SettingRead:
    _require_permission(user, "system.settings.manage")
    result = await session.execute(select(SystemSetting).where(SystemSetting.key == key))
    s = result.scalar_one_or_none()
    if not s:
        raise NotFoundError(f"Setting '{key}' not found")
    s.value = payload.value
    session.add(s)
    await session.commit()
    await session.refresh(s)
    return SettingRead(
        id=s.id,
        key=s.key,
        value=s.value,
        description=s.description,
        is_public=s.is_public,
        created_at=s.created_at,
    )
