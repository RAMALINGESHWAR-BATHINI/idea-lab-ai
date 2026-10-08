"""People models: Faculty, Staff, Student, IdeaLabMember."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AccessLevel


class Faculty(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A faculty member."""

    __tablename__ = "faculty"

    full_name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    employee_code: Mapped[str | None] = mapped_column(String(40), nullable=True)

    department_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    department: Mapped["Department | None"] = relationship(  # noqa: F821
        back_populates="faculty", lazy="joined"
    )

    designation: Mapped[str | None] = mapped_column(String(120), nullable=True)
    specialization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    research_interests: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    office_location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    is_hod: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    access_level: Mapped[AccessLevel] = mapped_column(
        SAEnum(AccessLevel, name="access_level"),
        default=AccessLevel.PUBLIC,
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Faculty {self.full_name}>"


class Staff(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A non-teaching staff member."""

    __tablename__ = "staff"

    full_name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    employee_code: Mapped[str | None] = mapped_column(String(40), nullable=True)

    department_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    department: Mapped["Department | None"] = relationship(  # noqa: F821
        back_populates="staff", lazy="joined"
    )

    designation: Mapped[str | None] = mapped_column(String(120), nullable=True)
    responsibilities: Mapped[str | None] = mapped_column(Text, nullable=True)
    access_level: Mapped[AccessLevel] = mapped_column(
        SAEnum(AccessLevel, name="access_level"),
        default=AccessLevel.INTERNAL,
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Staff {self.full_name}>"


class Student(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A student. Treated as restricted personal data by default."""

    __tablename__ = "students"

    full_name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    roll_number: Mapped[str | None] = mapped_column(
        String(40), unique=True, nullable=True
    )
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)

    department_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    department: Mapped["Department | None"] = relationship(  # noqa: F821
        back_populates="students", lazy="joined"
    )

    program: Mapped[str | None] = mapped_column(String(120), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mentor_faculty_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("faculty.id", ondelete="SET NULL"),
        nullable=True,
    )
    access_level: Mapped[AccessLevel] = mapped_column(
        SAEnum(AccessLevel, name="access_level"),
        default=AccessLevel.RESTRICTED,
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Student {self.full_name}>"


class IdeaLabMember(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A member of the IdeaLab (student/faculty/staff participant)."""

    __tablename__ = "idealab_members"

    full_name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    department_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    department: Mapped["Department | None"] = relationship(  # noqa: F821
        back_populates="members", lazy="joined"
    )

    role_title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    team: Mapped[str | None] = mapped_column(String(120), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    joined_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    access_level: Mapped[AccessLevel] = mapped_column(
        SAEnum(AccessLevel, name="access_level"),
        default=AccessLevel.INTERNAL,
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<IdeaLabMember {self.full_name}>"
