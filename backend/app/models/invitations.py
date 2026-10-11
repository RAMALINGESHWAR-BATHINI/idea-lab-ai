"""Invitation and access-grant models."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import GrantType, InvitationStatus


class Invitation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single-use, expiring, revocable access code (Method B)."""

    __tablename__ = "invitations"

    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    code_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    role_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
    )
    role: Mapped["Role | None"] = relationship()  # noqa: F821
    permissions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    scope: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[InvitationStatus] = mapped_column(
        SAEnum(InvitationStatus, name="invitation_status"),
        default=InvitationStatus.PENDING,
        nullable=False,
    )
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    used_at: Mapped[datetime | None] = mapped_column(nullable=True)
    used_by: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    user: Mapped["User | None"] = relationship(foreign_keys=[used_by])  # noqa: F821

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    max_uses: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<Invitation status={self.status} email={self.email}>"


class AccessGrant(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Central record of an access grant issued via any method (A, B, or C)."""

    __tablename__ = "access_grants"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    user: Mapped["User"] = relationship(foreign_keys=[user_id])  # noqa: F821

    grant_type: Mapped[GrantType] = mapped_column(
        SAEnum(GrantType, name="grant_type"),
        nullable=False,
    )
    scope: Mapped[str] = mapped_column(String(200), nullable=False)
    permissions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    approver_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approver: Mapped["User | None"] = relationship(
        foreign_keys=[approver_id]
    )
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"<AccessGrant type={self.grant_type} user={self.user_id}>"
