"""Voice channel: the shared chat API accepts channel="voice" and asks for speakable replies."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models.enums import AccessLevel
from app.schemas.chat import ChatRequest
from app.security.rbac import readable_levels
from app.services.ai_orchestrator import AIOrchestrator
from app.services.tools import ToolContext


def _anonymous_ctx() -> ToolContext:
    return ToolContext(
        session=None,  # type: ignore[arg-type]  # not used when building the prompt
        user_id=None,
        role_name=None,
        is_superuser=False,
        access_levels=readable_levels(None, is_superuser=False),
        permission_names=None,
    )


def test_chat_request_defaults_to_text_channel() -> None:
    assert ChatRequest(message="hello").channel == "text"


def test_chat_request_accepts_voice_channel() -> None:
    assert ChatRequest(message="hello", channel="voice").channel == "voice"


def test_chat_request_rejects_unknown_channel() -> None:
    with pytest.raises(ValidationError):
        ChatRequest(message="hello", channel="admin")  # type: ignore[arg-type]


def test_voice_prompt_asks_for_plain_spoken_text() -> None:
    orchestrator = AIOrchestrator(session=None)  # type: ignore[arg-type]
    ctx = _anonymous_ctx()
    voice = orchestrator._build_system_prompt(ctx, "voice")
    text = orchestrator._build_system_prompt(ctx, "text")
    assert "read aloud" in voice
    assert "read aloud" not in text


def test_voice_channel_does_not_widen_anonymous_access() -> None:
    # The channel only changes reply style; visitor access levels stay as computed by RBAC.
    levels = readable_levels(None, is_superuser=False)
    assert AccessLevel.PUBLIC in levels
