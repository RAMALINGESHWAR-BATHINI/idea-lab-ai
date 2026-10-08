"""Gemini implementation of :class:`ChatProvider` and grounded web search.

Uses the official ``google-genai`` SDK. Model ids are supplied by config only.
"""
from __future__ import annotations

from typing import Any

from google import genai
from google.genai import types

from app.ai.base import (
    ChatTurn,
    ModelReply,
    Source,
    ToolInvocation,
    ToolSpec,
)
from app.core.config import settings
from app.core.errors import ProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)

_TEXT_ROLE = {"user": "user", "tool": "user", "assistant": "model", "system": "user"}


class GeminiProvider:
    """Reasoning + tool calling + Google Search grounding via Gemini."""

    name = "gemini"

    def __init__(
        self,
        api_key: str | None = None,
        text_model: str | None = None,
    ) -> None:
        self._api_key = api_key or settings.gemini_api_key
        self.text_model = text_model or settings.gemini_text_model
        if not self._api_key:
            raise ProviderError(
                "GEMINI_API_KEY is not configured; set it in backend/.env"
            )
        self._client = genai.Client(api_key=self._api_key)

    # ---- construction helpers -------------------------------------------

    @staticmethod
    def _schema_from(spec: ToolSpec) -> types.Schema:
        properties: dict[str, types.Schema] = {}
        required: list[str] = []
        for param in spec.parameters:
            properties[param.name] = types.Schema(
                type=param.type,
                description=param.description,
                enum=param.enum,
            )
            if param.required:
                required.append(param.name)
        return types.Schema(
            type="object",
            properties=properties,
            required=required or None,
        )

    def _build_tools(
        self, tools: list[ToolSpec] | None
    ) -> list[types.Tool] | None:
        if not tools:
            return None
        declarations = [
            types.FunctionDeclaration(
                name=spec.name,
                description=spec.description,
                parameters=self._schema_from(spec),
            )
            for spec in tools
        ]
        return [types.Tool(function_declarations=declarations)]

    @staticmethod
    def _to_contents(messages: list[ChatTurn]) -> list[types.Content]:
        return [
            types.Content(
                role=_TEXT_ROLE.get(turn.role, "user"),
                parts=[types.Part(text=turn.content)],
            )
            for turn in messages
        ]

    # ---- ChatProvider ----------------------------------------------------

    async def generate(
        self,
        *,
        system_instruction: str,
        messages: list[ChatTurn],
        tools: list[ToolSpec] | None = None,
    ) -> ModelReply:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=self._build_tools(tools),
            temperature=0.7,
        )
        try:
            response = await self._client.aio.models.generate_content(
                model=self.text_model,
                contents=self._to_contents(messages),
                config=config,
            )
        except Exception as exc:  # noqa: BLE001 - surface as provider error
            logger.error("gemini_generate_failed", error=str(exc))
            raise ProviderError(f"Gemini request failed: {exc}") from exc
        return self._parse(response)

    async def generate_grounded(
        self,
        *,
        system_instruction: str,
        messages: list[ChatTurn],
    ) -> ModelReply:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.4,
        )
        try:
            response = await self._client.aio.models.generate_content(
                model=self.text_model,
                contents=self._to_contents(messages),
                config=config,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("gemini_grounded_failed", error=str(exc))
            raise ProviderError(f"Gemini search-grounded request failed: {exc}") from exc
        reply = self._parse(response)
        reply.sources = self._extract_sources(response)
        return reply

    # ---- parsing ---------------------------------------------------------

    @staticmethod
    def _parse(response: Any) -> ModelReply:
        tool_calls: list[ToolInvocation] = []
        for call in getattr(response, "function_calls", None) or []:
            tool_calls.append(
                ToolInvocation(
                    name=call.name,
                    arguments=dict(call.args or {}),
                )
            )
        text: str | None = None
        try:
            text = response.text
        except Exception:  # noqa: BLE001 - text may be absent on tool-only replies
            text = None
        return ModelReply(text=text, tool_calls=tool_calls)

    @staticmethod
    def _extract_sources(response: Any) -> list[Source]:
        sources: list[Source] = []
        candidates = getattr(response, "candidates", None) or []
        for candidate in candidates:
            metadata = getattr(candidate, "grounding_metadata", None)
            if not metadata:
                continue
            for chunk in getattr(metadata, "grounding_chunks", None) or []:
                web = getattr(chunk, "web", None)
                if web and getattr(web, "uri", None):
                    sources.append(
                        Source(
                            title=getattr(web, "title", None),
                            url=web.uri,
                            snippet=getattr(web, "domain", None),
                        )
                    )
        # De-duplicate by URL while preserving order.
        seen: set[str] = set()
        unique: list[Source] = []
        for src in sources:
            if src.url not in seen:
                seen.add(src.url)
                unique.append(src)
        return unique

    # ---- model validation ------------------------------------------------

    async def list_available_models(self) -> set[str]:
        """Return the set of model ids the API key can access."""
        names: set[str] = set()
        try:
            pager = await self._client.aio.models.list()
            async for model in pager:
                model_name = getattr(model, "name", "") or ""
                names.add(model_name.split("/")[-1])
        except Exception as exc:  # noqa: BLE001 - validation is best-effort
            logger.warning("gemini_list_models_failed", error=str(exc))
        return names

    async def close(self) -> None:
        try:
            await self._client.aio.aclose()
        except Exception:  # noqa: BLE001 - best-effort cleanup
            pass
