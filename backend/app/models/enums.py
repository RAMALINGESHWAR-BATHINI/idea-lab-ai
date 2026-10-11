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

    # Core auth roles
    STUDENT = "student"
    FACULTY = "faculty"
    STAFF = "staff"
    IDEALAB_MEMBER = "idealab_member"
    ADMIN = "admin"
    # Institutional IdeaLab roles
    GLOBAL_ADMIN = "global_admin"
    IDEALAB_ADMIN = "idealab_admin"
    CHIEF_MENTOR = "chief_mentor"
    FACULTY_COORDINATOR = "faculty_coordinator"
    TECH_GURU = "tech_guru"
    STUDENT_COORDINATOR = "student_coordinator"
    STUDENT_AMBASSADOR = "student_ambassador"
    CONTRIBUTOR = "contributor"
    PUBLIC_VISITOR = "public_visitor"


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


class EventStatus(str, enum.Enum):
    """Lifecycle state of an event."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class BookingStatus(str, enum.Enum):
    """Lifecycle state of an equipment booking."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class InvitationStatus(str, enum.Enum):
    """Lifecycle state of an invitation / access code."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class GrantType(str, enum.Enum):
    """How an access grant was issued."""

    EMAIL_VERIFICATION = "email_verification"
    INVITATION = "invitation"
    ADMIN_APPROVAL = "admin_approval"
    FACULTY_APPROVAL = "faculty_approval"


class DocumentProcessingStatus(str, enum.Enum):
    """Processing state of an uploaded document."""

    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"
