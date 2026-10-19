"""Chat schemas for the AI conversational interface."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatMessageBase(BaseModel):
    role: str = Field(description="e.g. user, assistant, tool, system")
    content: str | None = None
    tool_name: str | None = None
    tool_args: dict | None = None
    tool_result: dict | None = None
    sources: list | None = None
    finish_reason: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class ChatMessageRead(ChatMessageBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    tokens: int | None = None
    created_at: datetime


class ChatMessageCreate(ChatMessageBase):
    conversation_id: uuid.UUID | None = None


class ConversationMessageRead(BaseModel):
    id: uuid.UUID
    role: str
    content: str | None
    tool_name: str | None
    tool_args: dict | None
    tool_result: dict | None
    sources: list | None
    tokens: int | None
    created_at: datetime


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str | None
    channel: str
    last_activity_at: datetime
    is_active: bool
    messages: list[ConversationMessageRead] = []


class ConversationCreate(BaseModel):
    title: str | None = None
    channel: str = "text"


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    conversation_id: uuid.UUID | None = None
    model: str | None = None
    provider: str | None = None
    use_search: bool = True
    # "voice" asks for short, speakable replies (used by the voice assistant app).
    channel: Literal["text", "voice"] = "text"
    # Assistant mode: "idealab" for IdeaLab tools, "gemini" for general Q&A/web search, "auto" for AI-decided.
    mode: Literal["idealab", "gemini", "auto"] | None = None
    # Behavior policy for voice mode switching: "remember", "auto", "ask".
    behavior_policy: Literal["remember", "auto", "ask"] | None = None


class ChatResponse(BaseModel):
    content: str
    sources: list[dict[str, Any]]
    tool_calls: list[dict[str, Any]]
    conversation_id: str | None
    ai_available: bool
    mode: str | None = None
    behavior_policy: str | None = None
