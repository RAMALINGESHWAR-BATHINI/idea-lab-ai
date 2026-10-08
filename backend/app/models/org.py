"""Organizational models: Department, Organization."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AccessLevel

if TYPE_CHECKING:
    from app.models.people import Faculty, IdeaLabMember, Staff, Student


class Department(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An academic department (e.g. Computer Science and Engineering)."""

    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    building: Mapped[str | None] = mapped_column(String(120), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    access_level: Mapped[AccessLevel] = mapped_column(
        SAEnum(AccessLevel, name="access_level"),
        default=AccessLevel.PUBLIC,
        nullable=False,
    )

    faculty: Mapped[list["Faculty"]] = relationship(back_populates="department")
    staff: Mapped[list["Staff"]] = relationship(back_populates="department")
    students: Mapped[list["Student"]] = relationship(back_populates="department")
    members: Mapped[list["IdeaLabMember"]] = relationship(back_populates="department")

    def hod(self) -> "Faculty | None":
        """Return the head of department, if one is flagged."""
        for member in self.faculty:
            if member.is_hod:
                return member
        return None

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Department {self.code}>"


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A club, cell, lab or other organization within the institution."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    kind: Mapped[str | None] = mapped_column(String(80), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    access_level: Mapped[AccessLevel] = mapped_column(
        SAEnum(AccessLevel, name="access_level"),
        default=AccessLevel.PUBLIC,
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Organization {self.name}>"
