"""Audit logging service.

Writes security-relevant events to the ``audit_logs`` table. Designed to never
raise into the request path: audit failures are logged and swallowed so a
logging hiccup cannot break a user request.
"""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models.audit import AuditLog

logger = get_logger(__name__)

# Detail keys that must never be persisted verbatim.
_REDACT_KEYS = {
    "password",
    "hashed_password",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "secret",
    "authorization",
}


def _redact(detail: dict[str, Any] | None) -> dict[str, Any] | None:
    if not detail:
        return detail
    cleaned: dict[str, Any] = {}
    for key, value in detail.items():
        if key.lower() in _REDACT_KEYS:
            cleaned[key] = "[redacted]"
        elif isinstance(value, str) and len(value) > 2000:
            cleaned[key] = value[:2000] + "...[truncated]"
        else:
            cleaned[key] = value
    return cleaned


async def record_audit(
    session: AsyncSession,
    *,
    action: str,
    user_id: uuid.UUID | None = None,
    actor: str | None = None,
    resource: str | None = None,
    status: str = "success",
    ip_address: str | None = None,
    user_agent: str | None = None,
    request_id: str | None = None,
    latency_ms: float | None = None,
    detail: dict[str, Any] | None = None,
    is_error: bool = False,
    error_message: str | None = None,
) -> None:
    """Persist an audit entry (best-effort; never raises to the caller)."""
    if not settings.audit_enabled:
        return
    try:
        entry = AuditLog(
            user_id=user_id,
            actor=actor,
            action=action,
            resource=resource,
            status=status,
            ip_address=ip_address,
            user_agent=(user_agent[:500] if user_agent else None),
            request_id=request_id,
            latency_ms=latency_ms,
            detail=_redact(detail),
            is_error=is_error,
            error_message=error_message,
        )
        session.add(entry)
        await session.flush()
    except Exception as exc:  # pragma: no cover - audit must never break requests
        logger.warning("audit_write_failed", action=action, error=str(exc))
