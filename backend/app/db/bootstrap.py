"""Idempotent creation of built-in reference data (roles, permissions).

The initial Alembic migration creates the tables but ships no rows.
Registration needs the ``student`` role to exist, and the permission system
needs default permissions to function. This module creates all built-in roles
and permissions on first use.

Also provides a bootstrap script to create the first superuser and load
demo data.
"""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.auth import Permission, Role, User, role_permissions
from app.models.enums import RoleName

# Default permission set: <resource>.<action>
DEFAULT_PERMISSIONS: list[tuple[str, str]] = [
    # Events
    ("events.read", "Read event records"),
    ("events.create", "Create event drafts"),
    ("events.update", "Update event records"),
    ("events.publish", "Publish events"),
    ("events.review", "Review and approve events"),
    # Projects
    ("projects.read", "Read project records"),
    ("projects.create", "Create project drafts"),
    ("projects.update", "Update project records"),
    ("projects.publish", "Publish projects"),
    ("projects.review", "Review and approve projects"),
    # People
    ("people.read", "Read people profiles"),
    ("people.manage", "Manage people profiles"),
    # Equipment
    ("equipment.read", "Read equipment records"),
    ("equipment.manage", "Manage equipment inventory"),
    ("equipment.book", "Book equipment"),
    ("equipment.approve_booking", "Approve equipment bookings"),
    # Documents
    ("documents.upload", "Upload documents"),
    ("documents.read", "Read documents"),
    ("documents.manage", "Manage documents"),
    # AI
    ("ai.tools.execute", "Execute AI tools"),
    ("ai.tools.execute_sensitive", "Execute sensitive AI actions"),
    ("ai.chat", "Use the AI chat interface"),
    ("ai.voice", "Use voice interface"),
    # Users / Roles
    ("users.invite", "Invite users"),
    ("users.manage", "Manage user accounts"),
    ("users.deactivate", "Deactivate user accounts"),
    ("roles.assign", "Assign roles to users"),
    ("roles.manage", "Manage roles and permissions"),
    # Audit / Reports
    ("audit.read", "Read audit logs"),
    ("reports.export", "Export reports"),
    ("reports.read", "Read reports"),
    # Settings
    ("system.settings.manage", "Manage system settings"),
    # Devices
    ("devices.manage", "Manage device tokens"),
    ("devices.register", "Register new devices"),
    # Invitations
    ("invitations.manage", "Create and manage invitations"),
    ("invitations.redeem", "Redeem access codes"),
    # Access grants
    ("access_grants.read", "Read access grants"),
    ("access_grants.manage", "Manage access grants"),
    # Web search
    ("web.search", "Perform web searches"),
    ("web.fetch", "Fetch web pages"),
]

# Role → list of permission names assigned at creation.
# Anonymous users get no role; public_visitor is for registered but unprivileged users.
ROLE_PERMISSIONS: dict[str, list[str]] = {
    RoleName.STUDENT.value: [
        "events.read",
        "projects.read",
        "people.read",
        "equipment.read",
        "documents.read",
        "ai.chat",
        "invitations.redeem",
    ],
    RoleName.FACULTY.value: [
        "events.read",
        "events.create",
        "events.update",
        "projects.read",
        "projects.create",
        "projects.update",
        "people.read",
        "equipment.read",
        "equipment.book",
        "documents.read",
        "documents.upload",
        "ai.chat",
        "ai.tools.execute",
        "web.search",
        "web.fetch",
        "reports.read",
    ],
    RoleName.STAFF.value: [
        "events.read",
        "projects.read",
        "people.read",
        "equipment.read",
        "equipment.book",
        "documents.read",
        "ai.chat",
    ],
    RoleName.IDEALAB_MEMBER.value: [
        "events.read",
        "events.create",
        "projects.read",
        "projects.create",
        "people.read",
        "equipment.read",
        "equipment.book",
        "documents.read",
        "documents.upload",
        "ai.chat",
        "ai.tools.execute",
        "web.search",
    ],
    # Institutional IdeaLab roles
    RoleName.PUBLIC_VISITOR.value: [
        "events.read",
        "projects.read",
        "people.read",
        "equipment.read",
        "ai.chat",
    ],
    RoleName.CONTRIBUTOR.value: [
        "events.read",
        "events.create",
        "projects.read",
        "projects.create",
        "people.read",
        "equipment.read",
        "documents.read",
        "documents.upload",
        "ai.chat",
        "ai.tools.execute",
    ],
    RoleName.STUDENT_COORDINATOR.value: [
        "events.read",
        "events.create",
        "events.update",
        "events.publish",
        "projects.read",
        "projects.create",
        "projects.update",
        "people.read",
        "equipment.read",
        "equipment.book",
        "documents.read",
        "documents.upload",
        "ai.chat",
        "ai.tools.execute",
        "web.search",
        "reports.read",
        "invitations.manage",
    ],
    RoleName.STUDENT_AMBASSADOR.value: [
        "events.read",
        "projects.read",
        "people.read",
        "equipment.read",
        "equipment.book",
        "documents.read",
        "ai.chat",
        "web.search",
    ],
    RoleName.TECH_GURU.value: [
        "events.read",
        "events.create",
        "events.update",
        "events.publish",
        "projects.read",
        "projects.create",
        "projects.update",
        "projects.review",
        "projects.publish",
        "people.read",
        "people.manage",
        "equipment.read",
        "equipment.manage",
        "documents.read",
        "documents.upload",
        "documents.manage",
        "ai.chat",
        "ai.tools.execute",
        "ai.tools.execute_sensitive",
        "web.search",
        "web.fetch",
        "reports.read",
        "reports.export",
    ],
    RoleName.FACULTY_COORDINATOR.value: [
        "events.read",
        "events.create",
        "events.update",
        "events.review",
        "events.publish",
        "projects.read",
        "projects.create",
        "projects.update",
        "projects.review",
        "projects.publish",
        "people.read",
        "people.manage",
        "equipment.read",
        "equipment.manage",
        "documents.read",
        "documents.upload",
        "documents.manage",
        "ai.chat",
        "ai.tools.execute",
        "ai.tools.execute_sensitive",
        "web.search",
        "web.fetch",
        "reports.read",
        "reports.export",
        "users.manage",
        "roles.assign",
        "audit.read",
        "invitations.manage",
    ],
    RoleName.CHIEF_MENTOR.value: [
        "events.read", "events.create", "events.update", "events.review",
        "events.publish", "projects.read", "projects.create", "projects.update",
        "projects.review", "projects.publish", "people.read", "people.manage",
        "equipment.read", "equipment.manage", "documents.read",
        "documents.upload", "documents.manage", "ai.chat",
        "ai.tools.execute", "ai.tools.execute_sensitive", "web.search",
        "web.fetch", "reports.read", "reports.export", "users.manage",
        "users.deactivate", "roles.assign", "roles.manage", "audit.read",
        "invitations.manage", "access_grants.read", "access_grants.manage",
        "devices.manage", "system.settings.manage",
    ],
    RoleName.IDEALAB_ADMIN.value: [
        "events.read", "events.create", "events.update", "events.review",
        "events.publish", "projects.read", "projects.create", "projects.update",
        "projects.review", "projects.publish", "people.read", "people.manage",
        "equipment.read", "equipment.manage", "equipment.approve_booking",
        "documents.read", "documents.upload", "documents.manage",
        "ai.chat", "ai.tools.execute", "ai.tools.execute_sensitive",
        "web.search", "web.fetch", "reports.read", "reports.export",
        "users.manage", "users.deactivate", "roles.assign", "audit.read",
        "invitations.manage", "access_grants.read", "access_grants.manage",
        "devices.manage",
    ],
    RoleName.GLOBAL_ADMIN.value: [p[0] for p in DEFAULT_PERMISSIONS],
    RoleName.ADMIN.value: [p[0] for p in DEFAULT_PERMISSIONS],
}


async def ensure_default_roles(session: AsyncSession) -> dict[str, Role]:
    """Create any missing built-in roles and return all of them keyed by name."""
    result = await session.execute(select(Role))
    roles: dict[str, Role] = {role.name: role for role in result.scalars()}

    missing = False
    descriptions: dict[str, str] = {
        RoleName.STUDENT.value: "Default role for registered students.",
        RoleName.FACULTY.value: "College faculty and mentors.",
        RoleName.STAFF.value: "Institutional staff.",
        RoleName.IDEALAB_MEMBER.value: "Active IdeaLab participants.",
        RoleName.ADMIN.value: "Administrator with full access.",
        RoleName.GLOBAL_ADMIN.value: "Global administrator — full system access.",
        RoleName.IDEALAB_ADMIN.value: "IdeaLab administrator — full operational access.",
        RoleName.CHIEF_MENTOR.value: "Chief mentor of the IdeaLab.",
        RoleName.FACULTY_COORDINATOR.value: "Faculty coordinator for IdeaLab activities.",
        RoleName.TECH_GURU.value: "Technical lead / tech guru.",
        RoleName.STUDENT_COORDINATOR.value: "Student coordinator for IdeaLab activities.",
        RoleName.STUDENT_AMBASSADOR.value: "Student ambassador / volunteer.",
        RoleName.CONTRIBUTOR.value: "Contributor who can submit content for review.",
        RoleName.PUBLIC_VISITOR.value: "Registered visitor with minimal access.",
    }

    all_role_names = list(RoleName)
    for name in all_role_names:
        if name.value not in roles:
            role = Role(
                name=name.value,
                description=descriptions.get(name.value, f"Role: {name.value}"),
                is_system=True,
            )
            session.add(role)
            roles[name.value] = role
            missing = True

    if missing:
        await session.flush()
    return roles


async def ensure_default_permissions(session: AsyncSession) -> dict[str, Permission]:
    """Create any missing permissions and return them keyed by name."""
    result = await session.execute(select(Permission))
    perms: dict[str, Permission] = {p.name: p for p in result.scalars()}

    missing = False
    for name, desc in DEFAULT_PERMISSIONS:
        if name not in perms:
            perm = Permission(name=name, description=desc)
            session.add(perm)
            perms[name] = perm
            missing = True

    if missing:
        await session.flush()
    return perms


async def assign_role_permissions(
    session: AsyncSession,
    roles: dict[str, Role],
    perms: dict[str, Permission],
) -> None:
    """Assign default permissions to default roles (idempotent)."""
    for role_name, perm_names in ROLE_PERMISSIONS.items():
        if role_name not in roles:
            continue
        role = roles[role_name]
        existing_perms = {p.name for p in role.permissions}
        for perm_name in perm_names:
            if perm_name in perms and perm_name not in existing_perms:
                role.permissions.append(perms[perm_name])

    await session.flush()


async def bootstrap_database(session: AsyncSession) -> dict[str, Any]:
    """Create all default roles, permissions, and assign them.

    Safe to call repeatedly.
    """
    roles = await ensure_default_roles(session)
    perms = await ensure_default_permissions(session)
    await assign_role_permissions(session, roles, perms)
    await session.commit()
    return {
        "roles": list(roles.keys()),
        "permissions": list(perms.keys()),
    }


async def create_superuser(
    session: AsyncSession,
    email: str,
    password: str,
    full_name: str = "System Administrator",
) -> User:
    """Create (or update) a superuser account for bootstrap purposes.

    Only works if no superuser exists yet (or is called explicitly).
    """
    existing = await session.scalar(select(User).where(User.email == email))
    if existing is not None:
        if existing.is_superuser:
            return existing
        existing.is_superuser = True
        existing.hashed_password = hash_password(password)
        existing.is_active = True
        await session.commit()
        return existing

    roles = await ensure_default_roles(session)
    admin_role = roles.get(RoleName.ADMIN.value) or roles.get(RoleName.GLOBAL_ADMIN.value)

    user = User(
        email=email.lower().strip(),
        hashed_password=hash_password(password),
        full_name=full_name,
        role_id=admin_role.id if admin_role else None,
        is_active=True,
        is_superuser=True,
        is_email_verified=True,
    )
    session.add(user)
    await session.commit()
    return user


def _main() -> None:
    """CLI entry: bootstrap the database with roles, permissions, and an admin."""
    from app.db.session import get_engine, get_session_factory
    from app.db.session import dispose_engine

    email = input("Admin email: ").strip()
    password = input("Admin password (min 8 chars): ").strip()
    full_name = input("Admin full name: ").strip() or "System Administrator"

    if len(password) < 8:
        print("Password must be at least 8 characters.")
        sys.exit(1)

    async def _run() -> None:
        engine = get_engine()
        factory = get_session_factory()
        async with factory() as session:
            result = await bootstrap_database(session)
            print(f"Created {len(result['roles'])} roles and {len(result['permissions'])} permissions.")
            user = await create_superuser(session, email, password, full_name)
            print(f"Superuser created: {user.email} (id={user.id})")

    asyncio.run(_run())
