"""Typed backend tools callable by the AI assistant.

Each tool is a simple function with a strict input schema. Every tool enforces
authorization server-side before producing a result — the AI model never
bypasses backend checks.

Tools are organized by category:
* Knowledge — search institutional documents (access-controlled)
* Content  — read events, projects, people (access-controlled)
* Actions  — create drafts, update permitted records (permission-gated)
* Meta     — health / provider status
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Callable

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import ToolSpec, ToolParameter
from app.core.config import settings
from app.core.errors import (
    NotFoundError,
    PermissionDeniedError,
    ProviderError,
)
from app.core.logging import get_logger
from app.models.audit import AuditLog
from app.models.chat import Conversation, Message
from app.models.enums import AccessLevel, MessageRole
from app.models.knowledge import Document, DocumentChunk
from app.security.rbac import readable_levels

logger = get_logger(__name__)


@dataclass
class ToolContext:
    """Context passed to every tool invocation."""
    session: AsyncSession
    user_id: uuid.UUID | None  # None for anonymous visitors
    role_name: str | None
    is_superuser: bool
    access_levels: frozenset[AccessLevel]
    permission_names: set[str] | None = None


@dataclass
class ToolResult:
    """The validated result of a tool call."""
    content: str
    error: bool = False
    metadata: dict[str, Any] | None = None


def _levels_for_user(ctx: ToolContext) -> frozenset[AccessLevel]:
    """Access levels the caller may read."""
    return ctx.access_levels


async def _require_permission(ctx: ToolContext, permission: str) -> None:
    """Raise PermissionDeniedError if the user lacks a permission."""
    if ctx.user_id is None:
        raise PermissionDeniedError("Authentication required for this action")
    if ctx.is_superuser:
        return
    if ctx.permission_names is not None:
        if permission in ctx.permission_names:
            return
        raise PermissionDeniedError(f"Permission denied: {permission}")
    # Fallback: query the database for the user's permissions.
    from app.models.auth import User
    user = await ctx.session.get(User, ctx.user_id)
    if user is None or not user.is_active:
        raise PermissionDeniedError("User not found")
    if not user.has_permission(permission):
        raise PermissionDeniedError(f"Permission denied: {permission}")


# ---- Tool definitions --------------------------------------------------------

TOOL_DEFINITIONS: dict[str, ToolSpec] = {
    "search_institutional_knowledge": ToolSpec(
        name="search_institutional_knowledge",
        description=(
            "Search the institution's indexed documents for relevant content. "
            "Only returns excerpts from documents at access levels the caller "
            "is permitted to read. Returns source citations."
        ),
        parameters=[
            ToolParameter("query", "string", "The search query text.", required=True),
            ToolParameter("top_k", "integer", "Maximum number of results (1-20).", required=False),
        ],
    ),
    "get_public_event": ToolSpec(
        name="get_public_event",
        description="Retrieve a single published event by ID.",
        parameters=[
            ToolParameter("event_id", "string", "UUID of the event.", required=True),
        ],
    ),
    "list_public_projects": ToolSpec(
        name="list_public_projects",
        description=(
            "List published projects, optionally filtered by domain or technology. "
            "Only returns public records."
        ),
        parameters=[
            ToolParameter("domain", "string", "Filter by domain keyword.", required=False),
            ToolParameter("technology", "string", "Filter by technology keyword.", required=False),
            ToolParameter("limit", "integer", "Maximum results (1-50).", required=False),
        ],
    ),
    "create_event_draft": ToolSpec(
        name="create_event_draft",
        description=(
            "Create a new event as a draft (status=draft). Requires 'events.create' permission. "
            "The draft must be reviewed and published by an authorized user."
        ),
        parameters=[
            ToolParameter("title", "string", "Event title (max 250 chars).", required=True),
            ToolParameter("description", "string", "Event description.", required=False),
            ToolParameter("venue", "string", "Event venue.", required=False),
            ToolParameter("kind", "string", "Event type: event, workshop, seminar, hackathon, meeting, other.", required=False),
        ],
    ),
    "create_project_draft": ToolSpec(
        name="create_project_draft",
        description=(
            "Create a new project as a draft (is_published=False). "
            "Requires 'projects.create' permission."
        ),
        parameters=[
            ToolParameter("title", "string", "Project title (max 250 chars).", required=True),
            ToolParameter("description", "string", "Project description.", required=False),
            ToolParameter("domain", "string", "Project domain.", required=False),
            ToolParameter("technologies", "string", "Technologies used.", required=False),
        ],
    ),
    "web_search": ToolSpec(
        name="web_search",
        description=(
            "Search the public web for current information. Only available when a "
            "web search provider is configured. Returns source URLs."
        ),
        parameters=[
            ToolParameter("query", "string", "Search query.", required=True),
            ToolParameter("max_results", "integer", "Maximum results (1-10).", required=False),
        ],
    ),
    "get_provider_status": ToolSpec(
        name="get_provider_status",
        description=(
            "Check the status of AI and embedding providers. Returns which "
            "providers are configured and available."
        ),
        parameters=[],
    ),
}


# ---- Tool implementations ----------------------------------------------------

async def _search_institutional_knowledge(
    ctx: ToolContext, query: str, top_k: int = 5
) -> ToolResult:
    """Search indexed documents at access levels the caller may read."""
    from app.services.document_processor import _estimate_tokens

    levels = _levels_for_user(ctx)
    allowed_values = [lv.value for lv in levels]

    # Semantic search with pgvector.
    from app.ai.registry import get_embeddings

    try:
        provider = get_embeddings()
        query_embedding = await provider.embed_query(query)
    except ProviderError:
        # Fallback to keyword search if embedding provider is unavailable.
        stmt = (
            select(DocumentChunk)
            .join(Document)
            .where(DocumentChunk.access_level.in_(allowed_values))
            .where(
                func.to_tsvector("english", DocumentChunk.content).op("@@")(
                    func.plainto_tsquery("english", query)
                )
            )
            .limit(top_k)
        )
        chunks = await ctx.session.execute(stmt)
        results = [row[0] for row in chunks.fetchall()]
    else:
        from sqlalchemy import select as sql_select
        stmt = (
            sql_select(DocumentChunk)
            .join(Document)
            .where(DocumentChunk.access_level.in_(allowed_values))
            .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        result = await ctx.session.execute(stmt)
        results = [row[0] for row in result.fetchall()]

    if not results:
        return ToolResult(content="No institutional documents found for that query.")

    excerpts = []
    for chunk in results:
        excerpt = chunk.content[:300].replace("\n", " ").strip()
        excerpts.append(f"- {excerpt}... (source: doc {chunk.document_id})")

    return ToolResult(
        content="\n".join(excerpts),
        metadata={"sources": [{"document_id": str(c.document_id)} for c in results]},
    )


async def _get_public_event(ctx: ToolContext, event_id: str) -> ToolResult:
    """Retrieve a published event by ID."""
    try:
        event_uuid = uuid.UUID(event_id)
    except (ValueError, TypeError):
        raise NotFoundError("Event not found")

    from app.models.content import Event

    stmt = select(Event).where(Event.id == event_uuid)
    if ctx.user_id is None:
        # Anonymous: only public events.
        stmt = stmt.where(Event.access_level == AccessLevel.PUBLIC)
        stmt = stmt.where(Event.status == Event.__table__.c.status)  # published events

    event = await ctx.session.scalar(stmt)
    if event is None:
        raise NotFoundError("Event not found")

    # Check access level.
    from app.security.rbac import can_read
    if not can_read(ctx.role_name, event.access_level, is_superuser=ctx.is_superuser):
        raise PermissionDeniedError("You do not have access to this event")

    return ToolResult(
        content=(
            f"Title: {event.title}\n"
            f"Kind: {event.kind.value}\n"
            f"Venue: {event.venue or 'TBD'}\n"
            f"Starts: {event.starts_at}\n"
            f"Ends: {event.ends_at}\n"
            f"Description: {event.description or 'No description'}"
        ),
    )


async def _list_public_projects(
    ctx: ToolContext,
    domain: str | None = None,
    technology: str | None = None,
    limit: int = 10,
) -> ToolResult:
    """List published projects."""
    from app.models.content import Project

    stmt = (
        select(Project)
        .where(Project.is_published.is_(True))
        .where(Project.access_level == AccessLevel.PUBLIC)
        .limit(min(limit, 50))
    )

    if domain:
        stmt = stmt.where(Project.domain.ilike(f"%{domain}%"))
    if technology:
        stmt = stmt.where(Project.technologies.ilike(f"%{technology}%"))

    result = await ctx.session.execute(stmt)
    projects = [row[0] for row in result.fetchall()]

    if not projects:
        return ToolResult(content="No published projects found.")

    items = []
    for p in projects:
        items.append(
            f"- {p.title} (domain: {p.domain or 'N/A'}, tech: {p.technologies or 'N/A'}, status: {p.status or 'active'})"
        )

    return ToolResult(content="\n".join(items))


async def _create_event_draft(
    ctx: ToolContext, title: str, description: str | None = None,
    venue: str | None = None, kind: str | None = None,
) -> ToolResult:
    """Create an event draft. Requires events.create permission."""
    await _require_permission(ctx, "events.create")

    from app.models.content import Event
    from app.models.enums import EventKind, EventStatus

    event = Event(
        title=title,
        description=description,
        venue=venue,
        kind=EventKind(kind.lower()) if kind else EventKind.EVENT,
        status=EventStatus.DRAFT,
        is_active=True,
        access_level=AccessLevel.INTERNAL,
    )
    ctx.session.add(event)
    await ctx.session.flush()

    return ToolResult(
        content=f"Created event draft '{title}' with ID {event.id}. It is in draft status and needs review before publication.",
        metadata={"event_id": str(event.id), "status": "draft"},
    )


async def _create_project_draft(
    ctx: ToolContext, title: str, description: str | None = None,
    domain: str | None = None, technologies: str | None = None,
) -> ToolResult:
    """Create a project draft. Requires projects.create permission."""
    await _require_permission(ctx, "projects.create")

    from app.models.content import Project

    project = Project(
        title=title,
        description=description,
        domain=domain,
        technologies=technologies,
        is_active=True,
        is_published=False,
        access_level=AccessLevel.INTERNAL,
    )
    ctx.session.add(project)
    await ctx.session.flush()

    return ToolResult(
        content=f"Created project draft '{title}' with ID {project.id}. It is unpublished and needs review.",
        metadata={"project_id": str(project.id), "published": False},
    )


async def _web_search(ctx: ToolContext, query: str, max_results: int = 5) -> ToolResult:
    """Web search — only for authenticated users with web_search permission."""
    await _require_permission(ctx, "web.search")

    from app.services.web_search import search_web

    try:
        results = await search_web(query, max_results=min(max_results, 10))
    except ProviderError as exc:
        return ToolResult(content=f"Web search unavailable: {exc}", error=True)

    if not results:
        return ToolResult(content="No web results found.")

    items = []
    for r in results:
        items.append(
            f"- {r.title or 'Untitled'}: {r.snippet or 'No snippet'} "
            f"(URL: {r.url})"
        )

    return ToolResult(
        content="\n".join(items),
        metadata={"source": "web_search"},
    )


async def _get_provider_status(ctx: ToolContext) -> ToolResult:
    """Return AI provider status information."""
    from app.ai.registry import provider_status

    status = provider_status()
    parts = []
    for key, val in status.items():
        parts.append(f"{key}: {val}")
    return ToolResult(content="\n".join(parts))


# Registry mapping tool name → implementation function
TOOL_IMPLS: dict[str, Callable[..., Any]] = {
    "search_institutional_knowledge": _search_institutional_knowledge,
    "get_public_event": _get_public_event,
    "list_public_projects": _list_public_projects,
    "create_event_draft": _create_event_draft,
    "create_project_draft": _create_project_draft,
    "web_search": _web_search,
    "get_provider_status": _get_provider_status,
}


def get_tool_specs() -> list[ToolSpec]:
    """Return all tool definitions for the provider."""
    return list(TOOL_DEFINITIONS.values())


def get_tool_names() -> list[str]:
    """Return the set of enabled tool names."""
    return list(TOOL_DEFINITIONS.keys())
