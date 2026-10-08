"""Provider registry: selects and caches the configured AI providers."""
from __future__ import annotations

from app.ai.base import ChatProvider, EmbeddingProvider
from app.ai.embeddings import get_embedding_provider
from app.ai.gemini_provider import GeminiProvider
from app.ai.ollama_provider import OllamaProvider
from app.core.config import settings
from app.core.errors import ProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)

_chat_provider: ChatProvider | None = None
_embedding_provider: EmbeddingProvider | None = None
_initialised = False


def get_chat_provider() -> ChatProvider | None:
    """Return the active chat provider (Gemini preferred, else Ollama).

    Returns ``None`` when no provider is configured/available.
    """
    global _chat_provider, _initialised
    if _chat_provider is not None:
        return _chat_provider
    if _initialised and _chat_provider is None:
        return None

    _initialised = True

    if settings.gemini_api_key:
        try:
            _chat_provider = GeminiProvider()
            logger.info("chat_provider_selected", provider="gemini",
                        model=_chat_provider.text_model)
            return _chat_provider
        except ProviderError as exc:
            logger.warning("gemini_provider_unavailable", error=str(exc))

    if settings.ollama_enabled:
        _chat_provider = OllamaProvider()
        logger.info("chat_provider_selected", provider="ollama",
                    model=_chat_provider.model)
        return _chat_provider

    logger.warning("no_chat_provider_configured")
    return None


def get_embeddings() -> EmbeddingProvider:
    """Return the cached embedding provider."""
    global _embedding_provider
    if _embedding_provider is None:
        _embedding_provider = get_embedding_provider()
        logger.info(
            "embedding_provider_selected",
            provider=_embedding_provider.name,
            dimension=_embedding_provider.dimension,
        )
    return _embedding_provider


def provider_status() -> dict:
    """Return a summary of configured providers (safe to expose to the UI)."""
    provider = get_chat_provider()
    return {
        "chat_provider": provider.name if provider else None,
        "gemini_configured": bool(settings.gemini_api_key),
        "gemini_text_model": settings.gemini_text_model,
        "gemini_live_model": settings.gemini_live_model,
        "gemini_live_thinking_model": settings.gemini_live_thinking_model,
        "ollama_enabled": settings.ollama_enabled,
        "embedding_provider": settings.embedding_provider,
        "embedding_dimension": settings.embedding_dimension,
    }


async def validate_gemini_models() -> dict:
    """Check that configured Gemini model ids exist for this API key."""
    if not settings.gemini_api_key or not settings.gemini_verify_models_on_start:
        return {"checked": False}

    provider = GeminiProvider()
    try:
        available = await provider.list_available_models()
    finally:
        await provider.close()

    if not available:
        return {"checked": True, "available": False, "missing": []}

    configured = {
        "text": settings.gemini_text_model,
        "live": settings.gemini_live_model,
        "live_thinking": settings.gemini_live_thinking_model,
        "embedding": settings.gemini_embedding_model,
    }
    missing = [name for name in configured.values() if name not in available]
    if missing:
        logger.warning("gemini_models_missing", missing=missing)
    return {
        "checked": True,
        "available": True,
        "missing": missing,
        "configured": configured,
    }


async def reset_providers() -> None:
    """Dispose cached providers (used on shutdown and in tests)."""
    global _chat_provider, _embedding_provider, _initialised
    if _chat_provider is not None:
        try:
            await _chat_provider.close()
        except Exception:  # noqa: BLE001
            pass
    _chat_provider = None
    _embedding_provider = None
    _initialised = False
