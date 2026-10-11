"""Equipment / facilities models: Equipment, EquipmentBooking."""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AccessLevel, BookingStatus


class Equipment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A piece of institutional equipment or facility resource."""

    __tablename__ = "equipment"

    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    specifications: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str | None] = mapped_column(String(60), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    access_level: Mapped[AccessLevel] = mapped_column(
        SAEnum(AccessLevel, name="access_level"),
        default=AccessLevel.INTERNAL,
        nullable=False,
    )

    bookings: Mapped[list["EquipmentBooking"]] = relationship(
        back_populates="equipment",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Equipment {self.name}>"


class EquipmentBooking(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A booking request for equipment."""

    __tablename__ = "equipment_bookings"

    equipment_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("equipment.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    equipment: Mapped[Equipment] = relationship(back_populates="bookings")

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    user: Mapped["User | None"] = relationship()  # noqa: F821

    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_time: Mapped[str | None] = mapped_column(String(200), nullable=True)
    end_time: Mapped[str | None] = mapped_column(String(200), nullable=True)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[BookingStatus] = mapped_column(
        SAEnum(BookingStatus, name="booking_status"),
        default=BookingStatus.PENDING,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<EquipmentBooking eq={self.equipment_id} status={self.status}>"
