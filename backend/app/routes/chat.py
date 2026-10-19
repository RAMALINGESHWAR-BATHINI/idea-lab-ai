"""AI chat routes: conversational interface with tool calling and web search."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_user, get_optional_current_user
from app.core.errors import ProviderError
from app.db.session import get_session
from app.models.auth import User
from app.models.chat import Conversation, Message
from app.schemas.chat import ChatRequest
from app.services.ai_orchestrator import AIOrchestrator
from app.services.memory_service import add_memory, list_memories, delete_memory

router = APIRouter(tags=["ai"])

CurrentUser = Depends(get_current_user)
OptionalUser = Depends(get_optional_current_user)


@router.post("/chat")
async def chat(
    payload: ChatRequest,
    user: User | None = OptionalUser,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Non-streaming chat endpoint — full response returned after completion."""
    if not settings.ollama_enabled and not settings.gemini_api_key:
        raise ProviderError(
            "No AI provider configured. Set OLLAMA_ENABLED=true or provide GEMINI_API_KEY."
        )

    orchestrator = AIOrchestrator(session=session)
    response = await orchestrator.chat(
        user=user,
        message=payload.message,
        conversation_id=payload.conversation_id,
        channel=payload.channel,
        mode=payload.mode,
        behavior_policy=payload.behavior_policy,
    )
    return response


@router.get("/conversations")
async def list_conversations(
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """List the current user's conversations (most recent first)."""
    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.last_activity_at.desc())
    )
    conversations = list(result.scalars())
    response = []
    for conv in conversations:
        msg_result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at)
        )
        msgs = list(msg_result.scalars())
        response.append({
            "id": str(conv.id),
            "channel": conv.channel,
            "title": conv.title,
            "last_activity_at": conv.last_activity_at,
            "is_active": conv.is_active,
            "messages": [
                {
                    "id": str(m.id),
                    "role": m.role.value,
                    "content": m.content,
                    "tool_name": m.tool_name,
                    "tool_args": m.tool_args,
                    "tool_result": m.tool_result,
                    "sources": m.sources,
                    "tokens": m.tokens,
                    "created_at": m.created_at,
                }
                for m in msgs
            ],
        })
    return response


@router.get("/conversations/{conv_id}")
async def get_conversation(
    conv_id: uuid.UUID,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Return a single conversation with its message history."""
    conv = await session.get(Conversation, conv_id)
    if conv is None or conv.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    msg_result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
    )
    msgs = list(msg_result.scalars())
    return {
        "id": str(conv.id),
        "channel": conv.channel,
        "title": conv.title,
        "last_activity_at": conv.last_activity_at,
        "is_active": conv.is_active,
        "messages": [
            {
                "id": str(m.id),
                "role": m.role.value,
                "content": m.content,
                "tool_name": m.tool_name,
                "tool_args": m.tool_args,
                "tool_result": m.tool_result,
                "sources": m.sources,
                "tokens": m.tokens,
                "created_at": m.created_at,
            }
            for m in msgs
        ],
    }


@router.delete("/conversations/{conv_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conv_id: uuid.UUID,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> None:
    conv = await session.get(Conversation, conv_id)
    if conv is None or conv.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    await session.delete(conv)
    await session.commit()


@router.get("/memory")
async def get_memory(
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> list:
    """Retrieve the user's stored memory items."""
    memories = await list_memories(session=session, user_id=user.id)
    return [
        {
            "id": str(m.id),
            "content": m.content,
            "key": m.key,
            "scope": m.scope.value if m.scope else None,
            "source": m.source,
            "created_at": m.created_at,
        }
        for m in memories
    ]


@router.post("/memory", status_code=status.HTTP_201_CREATED)
async def store_memory(
    content: str,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    await add_memory(session=session, user_id=user.id, content=content)
    return {"status": "stored"}


@router.delete("/memory/{memory_id}")
async def clear_memory(
    memory_id: uuid.UUID,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    await delete_memory(session=session, user_id=user.id, memory_id=memory_id)
    return {"status": "deleted"}
