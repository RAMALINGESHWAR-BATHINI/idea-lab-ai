"""Embedding providers.

Default is local Ollama (private data never leaves the machine). Gemini
embeddings are available behind the same interface when configured.
"""
from __future__ import annotations

import httpx
from google import genai
from google.genai import types

from app.core.config import settings
from app.core.errors import ProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


class OllamaEmbeddingProvider:
    """Local embeddings via an Ollama embedding model (e.g. nomic-embed-text)."""

    name = "ollama"

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        dimension: int | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_embed_model
        self.dimension = dimension or settings.embedding_dimension
        self._timeout = timeout

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        body = {"model": self.model, "input": texts}
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(f"{self.base_url}/api/embed", json=body)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.error("ollama_embed_failed", error=str(exc))
            raise ProviderError(f"Ollama embeddings failed: {exc}") from exc
        embeddings = data.get("embeddings") or []
        return [list(map(float, vec)) for vec in embeddings]

    async def embed_query(self, text: str) -> list[float]:
        vectors = await self.embed([text])
        if not vectors:
            raise ProviderError("Ollama returned no embedding for the query")
        return vectors[0]


class GeminiEmbeddingProvider:
    """Cloud embeddings via Gemini (only use for non-private content)."""

    name = "gemini"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        dimension: int | None = None,
    ) -> None:
        key = api_key or settings.gemini_api_key
        if not key:
            raise ProviderError("GEMINI_API_KEY is required for Gemini embeddings")
        self._client = genai.Client(api_key=key)
        self.model = model or settings.gemini_embedding_model
        self.dimension = dimension or settings.embedding_dimension

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        contents = [
            types.Content(parts=[types.Part(text=text)]) for text in texts
        ]
        try:
            response = await self._client.aio.models.embed_content(
                model=self.model,
                contents=contents,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("gemini_embed_failed", error=str(exc))
            raise ProviderError(f"Gemini embeddings failed: {exc}") from exc
        result: list[list[float]] = []
        for embedding in getattr(response, "embeddings", None) or []:
            values = getattr(embedding, "values", None) or []
            result.append(list(map(float, values)))
        return result

    async def embed_query(self, text: str) -> list[float]:
        vectors = await self.embed([text])
        if not vectors:
            raise ProviderError("Gemini returned no embedding for the query")
        return vectors[0]


def get_embedding_provider():
    """Return the configured embedding provider instance."""
    if settings.embedding_provider == "gemini":
        return GeminiEmbeddingProvider()
    return OllamaEmbeddingProvider()
