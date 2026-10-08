"""Idempotent creation of built-in reference data (roles).

The initial Alembic migration creates the ``roles`` table but ships no rows.
Registration needs the ``student`` role to exist, so this module creates the
five built-in roles on first use. Safe to call repeatedly.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import Role
from app.models.enums import RoleName

_ROLE_DESCRIPTIONS: dict[str, str] = {
    RoleName.STUDENT.value: "Default role for registered students (public and internal data).",
    RoleName.FACULTY.value: "College faculty and mentors.",
    RoleName.STAFF.value: "Institutional staff.",
    RoleName.IDEALAB_MEMBER.value: "Active IdeaLab participants.",
    RoleName.ADMIN.value: "Administrator with full access.",
}


async def ensure_default_roles(session: AsyncSession) -> dict[str, Role]:
    """Create any missing built-in roles and return all of them keyed by name."""
    result = await session.execute(select(Role))
    roles: dict[str, Role] = {role.name: role for role in result.scalars()}

    missing = False
    for name, description in _ROLE_DESCRIPTIONS.items():
        if name not in roles:
            role = Role(name=name, description=description, is_system=True)
            session.add(role)
            roles[name] = role
            missing = True
    if missing:
        await session.flush()
    return roles