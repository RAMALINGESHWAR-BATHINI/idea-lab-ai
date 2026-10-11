"""ORM models.

Importing this package registers every table on ``Base.metadata`` so that
Alembic autogenerate and ``create_all`` see the full schema.
"""
from __future__ import annotations

from app.models.audit import AuditLog
from app.models.auth import Permission, Role, User, role_permissions
from app.models.chat import Conversation, Message
from app.models.content import Event, EventRegistration, Notice, Project, Workshop
from app.models.devices import DeviceToken
from app.models.enums import (
    AccessLevel,
    BookingStatus,
    DocumentProcessingStatus,
    DocumentType,
    EventKind,
    EventStatus,
    GrantType,
    InvitationStatus,
    MemoryScope,
    MessageRole,
    NoticePriority,
    RoleName,
)
from app.models.equipment import Equipment, EquipmentBooking
from app.models.knowledge import Document, DocumentChunk, Research, WebSource
from app.models.memory import UserMemory
from app.models.org import Department, Organization
from app.models.people import Faculty, IdeaLabMember, Staff, Student
from app.models.settings import SystemSetting
from app.models.invitations import AccessGrant, Invitation

__all__ = [
    # auth / rbac
    "User",
    "Role",
    "Permission",
    "role_permissions",
    "AccessGrant",
    "Invitation",
    # org
    "Department",
    "Organization",
    # people
    "Faculty",
    "Staff",
    "Student",
    "IdeaLabMember",
    # content
    "Project",
    "Event",
    "EventRegistration",
    "Workshop",
    "Notice",
    # equipment
    "Equipment",
    "EquipmentBooking",
    # knowledge
    "Document",
    "DocumentChunk",
    "Research",
    "WebSource",
    # memory
    "UserMemory",
    # chat
    "Conversation",
    "Message",
    # audit
    "AuditLog",
    # devices
    "DeviceToken",
    # settings
    "SystemSetting",
    # enums
    "AccessLevel",
    "RoleName",
    "DocumentType",
    "EventKind",
    "EventStatus",
    "NoticePriority",
    "MemoryScope",
    "MessageRole",
    "BookingStatus",
    "InvitationStatus",
    "GrantType",
    "DocumentProcessingStatus",
]
