"""Programme content models: Project, Event, Workshop, Notice."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AccessLevel, EventKind, NoticePriority


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A project developed in or around the IdeaLab."""

    __tablename__ = "projects"

    title: Mapped[str] = mapped_column(String(250), index=True, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(60), nullable=True)
    domain: Mapped[str | None] = mapped_column(String(120), nullable=True)
    technologies: Mapped[str | None] = mapped_column(Text, nullable=True)
    team_lead_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("idealab_members.id", ondelete="SET NULL"),
        nullable=True,
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    repo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    demo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    access_level: Mapped[AccessLevel] = mapped_column(
        SAEnum(AccessLevel, name="access_level"),
        default=AccessLevel.INTERNAL,
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Project {self.title}>"


class Event(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A scheduled event (hackathon, seminar, talk, ...)."""

    __tablename__ = "events"

    title: Mapped[str] = mapped_column(String(250), index=True, nullable=False)
    kind: Mapped[EventKind] = mapped_column(
        SAEnum(EventKind, name="event_kind"),
        default=EventKind.EVENT,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    venue: Mapped[str | None] = mapped_column(String(200), nullable=True)
    starts_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True, nullable=True
    )
    ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    organizer: Mapped[str | None] = mapped_column(String(200), nullable=True)
    registration_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    access_level: Mapped[AccessLevel] = mapped_column(
        SAEnum(AccessLevel, name="access_level"),
        default=AccessLevel.PUBLIC,
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Event {self.title}>"


class Workshop(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A training workshop or hands-on session."""

    __tablename__ = "workshops"

    title: Mapped[str] = mapped_column(String(250), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    trainer: Mapped[str | None] = mapped_column(String(200), nullable=True)
    venue: Mapped[str | None] = mapped_column(String(200), nullable=True)
    starts_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True, nullable=True
    )
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seats: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    access_level: Mapped[AccessLevel] = mapped_column(
        SAEnum(AccessLevel, name="access_level"),
        default=AccessLevel.PUBLIC,
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Workshop {self.title}>"


class Notice(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An institutional notice or announcement."""

    __tablename__ = "notices"

    title: Mapped[str] = mapped_column(String(250), index=True, nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[NoticePriority] = mapped_column(
        SAEnum(NoticePriority, name="notice_priority"),
        default=NoticePriority.NORMAL,
        nullable=False,
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    posted_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    effective_from: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    access_level: Mapped[AccessLevel] = mapped_column(
        SAEnum(AccessLevel, name="access_level"),
        default=AccessLevel.PUBLIC,
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Notice {self.title}>"
