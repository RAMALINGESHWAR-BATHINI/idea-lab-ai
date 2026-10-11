"""User memory service.

Manages per-user memory items with opt-in semantics. Memory items are scoped
to a user, session, or institution. Private data never leaves the machine
when using the local embedding provider.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.registry import get_embeddings
from app.core.config import settings
from app.core.errors import PermissionDeniedError
from app.core.logging import get_logger
from app.models.enums import AccessLevel, MemoryScope
from app.models.memory import UserMemory

logger = get_logger(__name__)


async def add_memory(
    session: AsyncSession,
    user_id: uuid.UUID,
    content: str,
    *,
    key: str | None = None,
    scope: MemoryScope = MemoryScope.USER,
    source: str = "explicit",
    expires_at: datetime | None = None,
) -> UserMemory:
    """Add a memory item for a user."""
    # Enforce per-user limit.
    count_stmt = select(func.count()).where(
        UserMemory.user_id == user_id,
        UserMemory.is_active.is_(True),
    )
    count = await session.scalar(count_stmt)
    if count >= settings.memory_max_items_per_user:
        # Evict oldest active memory.
        oldest_stmt = (
            select(UserMemory)
            .where(
                UserMemory.user_id == user_id,
                UserMemory.is_active.is_(True),
            )
            .order_by(UserMemory.created_at.asc())
            .limit(1)
        )
        oldest = await session.scalar(oldest_stmt)
        if oldest:
            oldest.is_active = False

    memory = UserMemory(
        user_id=user_id,
        scope=scope,
        key=key,
        content=content,
        source=source,
        access_level=AccessLevel.CONFIDENTIAL,
    )
    memory.embedding = None

    # Generate embedding only for USER scope, using local provider.
    if scope == MemoryScope.USER:
        try:
            provider = get_embeddings()
            emb = await provider.embed([content])
            if emb:
                memory.embedding = emb[0]
                memory.embedding_provider = provider.name
        except Exception as exc:  # noqa: BLE001
            logger.warning("memory_embedding_failed", error=str(exc))

    session.add(memory)
    await session.commit()
    return memory


async def list_memories(
    session: AsyncSession,
    user_id: uuid.UUID,
    *,
    scope: MemoryScope | None = None,
    limit: int = 50,
) -> list[UserMemory]:
    """List active memories for a user."""
    stmt = (
        select(UserMemory)
        .where(
            UserMemory.user_id == user_id,
            UserMemory.is_active.is_(True),
        )
        .order_by(UserMemory.created_at.desc())
        .limit(limit)
    )
    if scope:
        stmt = stmt.where(UserMemory.scope == scope)
    result = await session.execute(stmt)
    return list(result.scalars())


async def delete_memory(session: AsyncSession, user_id: uuid.UUID, memory_id: uuid.UUID) -> bool:
    """Delete (soft-delete) a memory item owned by the user."""
    stmt = (
        select(UserMemory)
        .where(
            UserMemory.id == memory_id,
            UserMemory.user_id == user_id,
            UserMemory.is_active.is_(True),
        )
    )
    memory = await session.scalar(stmt)
    if memory is None:
        raise PermissionDeniedError("Memory item not found or not accessible")
    memory.is_active = False
    await session.commit()
    return True


async def search_memories(
    session: AsyncSession,
    user_id: uuid.UUID,
    query: str,
    *,
    limit: int = 10,
) -> list[UserMemory]:
    """Search the user's memory using vector similarity."""
    try:
        provider = get_embeddings()
        query_emb = await provider.embed_query(query)
    except Exception as exc:  # noqa: BLE001
        logger.warning("memory_search_embedding_failed", error=str(exc))
        # Fallback to keyword search.
        stmt = (
            select(UserMemory)
            .where(
                UserMemory.user_id == user_id,
                UserMemory.is_active.is_(True),
                UserMemory.content.ilike(f"%{query}%"),
            )
            .order_by(UserMemory.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars())

    stmt = (
        select(UserMemory)
        .where(
            UserMemory.user_id == user_id,
            UserMemory.is_active.is_(True),
        )
        .order_by(UserMemory.embedding.cosine_distance(query_emb))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars())
