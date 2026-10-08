"""Local Ollama chat provider.

Serves as an offline / private fallback for reasoning when Gemini is not
configured or unavailable. Ollama has no web-search grounding, so
``generate_grounded`` fails explicitly rather than silently degrading.
"""
from __future__ import annotations

import httpx

from app.ai.base import ChatTurn, ModelReply, ToolSpec
from app.core.config import settings
from app.core.errors import ProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


class OllamaProvider:
    """A simple chat provider backed by a local Ollama server."""

    name = "ollama"

    def __init__(
        self,
        base_url: str | None = None,
        model: str = "llama3.2",
        timeout: float = 60.0,
    ) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model
        self._timeout = timeout

    async def generate(
        self,
        *,
        system_instruction: str,
        messages: list[ChatTurn],
        tools: list[ToolSpec] | None = None,
    ) -> ModelReply:
        # Ollama does not reliably support function calling across models, so we
        # answer directly and let the orchestrator decide when a Gemini provider
        # is required.
        payload_messages = [{"role": "system", "content": system_instruction}]
        for turn in messages:
            role = "assistant" if turn.role == "assistant" else "user"
            payload_messages.append({"role": role, "content": turn.content})

        body = {
            "model": self.model,
            "messages": payload_messages,
            "stream": False,
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=body)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.error("ollama_chat_failed", error=str(exc))
            raise ProviderError(f"Ollama request failed: {exc}") from exc

        text = (data.get("message") or {}).get("content")
        return ModelReply(text=text)

    async def generate_grounded(
        self,
        *,
        system_instruction: str,
        messages: list[ChatTurn],
    ) -> ModelReply:
        raise ProviderError(
            "The local Ollama provider cannot perform live web search grounding"
        )

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:  # noqa: BLE001
            return False

    async def close(self) -> None:
        return None
