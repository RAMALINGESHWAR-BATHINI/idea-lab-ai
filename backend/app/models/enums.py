"""Shared enumerations used across ORM models and schemas."""
from __future__ import annotations

import enum


class AccessLevel(str, enum.Enum):
    """Classification of an information asset.

    Drives whether a record may ever leave the institution: only ``PUBLIC``
    records are safe to expose to external services.
    """

    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"


class RoleName(str, enum.Enum):
    """Built-in role identifiers."""

    STUDENT = "student"
    FACULTY = "faculty"
    STAFF = "staff"
    IDEALAB_MEMBER = "idealab_member"
    ADMIN = "admin"


class DocumentType(str, enum.Enum):
    """Kinds of institutional documents."""

    POLICY = "policy"
    REPORT = "report"
    MINUTES = "minutes"
    RESEARCH = "research"
    GUIDELINE = "guideline"
    OTHER = "other"


class EventKind(str, enum.Enum):
    """Kinds of scheduled activities."""

    EVENT = "event"
    WORKSHOP = "workshop"
    SEMINAR = "seminar"
    HACKATHON = "hackathon"
    MEETING = "meeting"
    OTHER = "other"


class NoticePriority(str, enum.Enum):
    """Urgency of an institutional notice."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class MemoryScope(str, enum.Enum):
    """Lifetime/visibility of a stored memory item."""

    USER = "user"          # private to a single user
    SESSION = "session"    # valid for one conversation
    INSTITUTION = "institution"  # shared institutional fact (admin-managed)


class MessageRole(str, enum.Enum):
    """Who authored a conversation message."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
