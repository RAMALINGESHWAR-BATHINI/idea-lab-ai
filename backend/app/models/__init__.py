"""ORM models.

Importing this package registers every table on ``Base.metadata`` so that
Alembic autogenerate and ``create_all`` see the full schema.
"""
from __future__ import annotations

from app.models.audit import AuditLog
from app.models.auth import Permission, Role, User, role_permissions
from app.models.chat import Conversation, Message
from app.models.content import Event, Notice, Project, Workshop
from app.models.enums import (
    AccessLevel,
    DocumentType,
    EventKind,
    MemoryScope,
    MessageRole,
    NoticePriority,
    RoleName,
)
from app.models.knowledge import Document, DocumentChunk, Research, WebSource
from app.models.memory import UserMemory
from app.models.org import Department, Organization
from app.models.people import Faculty, IdeaLabMember, Staff, Student

__all__ = [
    # auth / rbac
    "User",
    "Role",
    "Permission",
    "role_permissions",
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
    "Workshop",
    "Notice",
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
    # enums
    "AccessLevel",
    "RoleName",
    "DocumentType",
    "EventKind",
    "NoticePriority",
    "MemoryScope",
    "MessageRole",
]
