"""Provider-agnostic interfaces and data transfer objects for the AI layer.

Two independent seams exist here:
  * ``ChatProvider``     - reasoning + tool calling + web grounding
  * ``EmbeddingProvider`` - vector embeddings for retrieval

Either can be swapped (Gemini <-> a local model) without touching the agent,
tools or API layers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Protocol, runtime_checkable

Role = Literal["system", "user", "assistant", "tool"]


@dataclass(slots=True)
class ChatTurn:
    """A single conversation turn passed to a provider."""

    role: Role
    content: str


@dataclass(slots=True)
class ToolParameter:
    """A single JSON-schema property for a tool."""

    name: str
    type: str
    description: str
    required: bool = True
    enum: list[str] | None = None


@dataclass(slots=True)
class ToolSpec:
    """Provider-facing description of a callable tool."""

    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)

    def to_json_schema(self) -> dict:
        """Return a JSON-schema object describing the tool's arguments."""
        properties: dict[str, dict] = {}
        required: list[str] = []
        for param in self.parameters:
            prop: dict = {"type": param.type, "description": param.description}
            if param.enum:
                prop["enum"] = param.enum
            properties[param.name] = prop
            if param.required:
                required.append(param.name)
        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }


@dataclass(slots=True)
class ToolInvocation:
    """A model's request to call a tool."""

    name: str
    arguments: dict
    call_id: str | None = None


@dataclass(slots=True)
class Source:
    """A citation returned by a grounded answer."""

    title: str | None
    url: str
    snippet: str | None = None


@dataclass(slots=True)
class ModelReply:
    """The result of a single provider generation."""

    text: str | None = None
    tool_calls: list[ToolInvocation] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    finish_reason: str | None = None

    @property
    def wants_tools(self) -> bool:
        return bool(self.tool_calls)


@runtime_checkable
class ChatProvider(Protocol):
    """A reasoning provider that supports tool calling and web grounding."""

    name: str

    async def generate(
        self,
        *,
        system_instruction: str,
        messages: list[ChatTurn],
        tools: list[ToolSpec] | None = None,
    ) -> ModelReply:
        """Generate a reply, optionally offering tools."""
        ...

    async def generate_grounded(
        self,
        *,
        system_instruction: str,
        messages: list[ChatTurn],
    ) -> ModelReply:
        """Generate a reply grounded with live web search."""
        ...

    async def close(self) -> None:
        ...


@runtime_checkable
class EmbeddingProvider(Protocol):
    """A provider of dense text embeddings."""

    name: str
    dimension: int

    async def embed(self, texts: list[str]) -> list[list[float]]:
        ...

    async def embed_query(self, text: str) -> list[float]:
        ...
