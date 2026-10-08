"""Application configuration.

All tunables live here and are sourced from environment variables (see
``backend/.env.example``).  Nothing in the codebase hardcodes model ids,
credentials or connection strings.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---- Application ----
    app_name: str = "IdeaLab AI"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    api_prefix: str = "/api"
    host: str = "127.0.0.1"
    port: int = 8000

    # ---- Security / auth ----
    secret_key: str = Field(
        default="change-me-in-production-please-use-a-long-random-value",
        description="HMAC key used to sign JWTs. MUST be overridden in production.",
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12
    refresh_token_expire_minutes: int = 60 * 24 * 30
    allow_registration: bool = True

    # ---- CORS ----
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    # ---- Database (PostgreSQL + pgvector only) ----
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/idealab"
    )
    db_echo: bool = False
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # ---- Gemini ----
    gemini_api_key: str = ""
    gemini_text_model: str = "gemini-3.8-flash"
    gemini_live_model: str = "gemini-3.8-live"
    gemini_live_thinking_model: str = "gemini-3.8-live-extended-thinking"
    gemini_embedding_model: str = "gemini-embedding-2"
    gemini_verify_models_on_start: bool = True

    # ---- Ollama (local / private inference + embeddings) ----
    ollama_enabled: bool = True
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_embed_model: str = "nomic-embed-text"

    # ---- Embeddings provider ----
    embedding_provider: Literal["ollama", "gemini"] = "ollama"
    embedding_dimension: int = 768

    # ---- Web intelligence / fetching ----
    fetch_timeout_seconds: float = 15.0
    fetch_max_bytes: int = 5_000_000
    fetch_max_redirects: int = 3
    fetch_user_agent: str = (
        "IdeaLabAI/0.1 (+https://idealab.local; contact: admin@idealab.local)"
    )
    web_search_results: int = 5
    ssrf_allow_private_hosts: bool = False

    # ---- Rate limiting ----
    rate_limit_default: str = "120/minute"
    rate_limit_auth: str = "20/minute"
    rate_limit_chat: str = "30/minute"
    rate_limit_voice: str = "20/minute"

    # ---- Memory ----
    memory_max_items_per_user: int = 500
    conversation_history_limit: int = 40

    # ---- Logging / audit ----
    log_level: str = "INFO"
    log_json: bool = False
    audit_enabled: bool = True

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        """Allow comma separated CORS origins in the environment."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def sync_database_url(self) -> str:
        """Sync SQLAlchemy URL (psycopg) for Alembic's offline mode."""
        return self.database_url.replace("+asyncpg", "")


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


settings = get_settings()
