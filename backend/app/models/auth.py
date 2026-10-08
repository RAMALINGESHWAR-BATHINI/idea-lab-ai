"""Authentication and RBAC models: User, Role, Permission."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

# Many-to-many association between roles and permissions.
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        PGUUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        PGUUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Permission(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A fine-grained capability (e.g. ``college.read``, ``memory.write``)."""

    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    roles: Mapped[list["Role"]] = relationship(
        secondary=role_permissions,
        back_populates="permissions",
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Permission {self.name}>"


class Role(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A named bundle of permissions assigned to users."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    permissions: Mapped[list[Permission]] = relationship(
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )
    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Role {self.name}>"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An authenticated principal."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    role_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
    )
    role: Mapped[Role | None] = relationship(back_populates="users", lazy="joined")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Link to an optional college identity (faculty/staff/student/member).
    person_ref: Mapped[str | None] = mapped_column(String(64), nullable=True)

    conversations: Mapped[list["Conversation"]] = relationship(  # noqa: F821
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @property
    def permission_names(self) -> set[str]:
        """Return the set of permission names granted via the role."""
        if self.is_superuser:
            return {"*"}
        if self.role is None:
            return set()
        return {perm.name for perm in self.role.permissions}

    def has_permission(self, name: str) -> bool:
        if self.is_superuser:
            return True
        return name in self.permission_names

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<User {self.email}>"
