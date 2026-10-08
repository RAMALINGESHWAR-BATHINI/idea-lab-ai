"""User memory model — a controlled, per-user long-term memory store."""
from __future__ import annotations

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, Enum as SAEnum
from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AccessLevel, MemoryScope


class UserMemory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single memory item.

    Memory is opt-in and user-controlled: items may be listed and deleted by
    their owner and are never sent to an external provider unless the user
    explicitly asks a question that requires them.
    """

    __tablename__ = "user_memories"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user: Mapped["User"] = relationship()  # noqa: F821

    scope: Mapped[MemoryScope] = mapped_column(
        SAEnum(MemoryScope, name="memory_scope"),
        default=MemoryScope.USER,
        nullable=False,
    )
    # Optional short label ("preferred_name", "course", ...).
    key: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    source: Mapped[str] = mapped_column(
        String(40), default="explicit", nullable=False
    )
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    embedding_provider: Mapped[str | None] = mapped_column(String(40), nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(settings.embedding_dimension), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    access_level: Mapped[AccessLevel] = mapped_column(
        SAEnum(AccessLevel, name="access_level"),
        default=AccessLevel.CONFIDENTIAL,
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<UserMemory {self.key or self.id}>"
