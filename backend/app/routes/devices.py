"""Device API routes for robot / ESP32 integration.

Versioned device API that supports:
* Device registration and provisioning
* Device authentication via token
* Device status and health
* Text requests and responses to the AI assistant
* Approved tool invocation through the backend
* Revocation and credential rotation

Devices use unique, revocable credentials — NOT a human administrator account.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import AuthenticationError, PermissionDeniedError
from app.core.audit import record_audit
from app.db.session import get_session
from app.models.devices import DeviceToken
from app.models.enums import GrantType, InvitationStatus
from app.models.invitations import AccessGrant, Invitation
from app.schemas.chat import ChatRequest

device_bearer = HTTPBearer(auto_error=False)

router = APIRouter(tags=["devices"])


async def get_device(
    credentials: HTTPAuthorizationCredentials | None = Depends(device_bearer),
    session: AsyncSession = Depends(get_session),
) -> DeviceToken:
    """Authenticate a device via its bearer token and return the DeviceToken."""
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Device credentials were not provided")

    raw_token = credentials.credentials
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    result = await session.execute(
        select(DeviceToken).where(DeviceToken.token_hash == token_hash)
    )
    device = result.scalar_one_or_none()

    if device is None:
        raise AuthenticationError("Invalid device credentials")

    if not device.is_active:
        raise AuthenticationError("Device is deactivated")

    if device.expires_at is not None and device.expires_at < datetime.now(timezone.utc):
        raise AuthenticationError("Device token has expired")

    if device.revoked_at is not None:
        raise AuthenticationError("Device token has been revoked")

    return device


@router.post("/register")
async def register_device(
    payload: dict,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Register a new device.

    Requires a valid invitation code (Method B — access grant via invitation).
    Returns the raw device token (displayed once at registration time only).
    """
    code = payload.get("code")
    if not code:
        raise AuthenticationError("An invitation code is required to register a device")

    code_hash = hashlib.sha256(code.encode()).hexdigest()
    result = await session.execute(
        select(Invitation).where(Invitation.code_hash == code_hash)
    )
    invitation = result.scalar_one_or_none()

    if invitation is None:
        raise AuthenticationError("Invalid invitation code")

    if invitation.status != InvitationStatus.PENDING:
        raise AuthenticationError("Invitation code has already been used or is no longer valid")

    if invitation.expires_at and invitation.expires_at < datetime.now(timezone.utc):
        raise AuthenticationError("Invitation code has expired")

    if invitation.used_count >= invitation.max_uses:
        raise AuthenticationError("Invitation code has been used the maximum number of times")

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    device = DeviceToken(
        name=payload.get("name", "Unnamed Device"),
        token_hash=token_hash,
        permissions=payload.get("permissions", invitation.permissions),
        access_level=payload.get("access_level", "public"),
        expires_at=payload.get("expires_at"),
        note=payload.get("note"),
    )
    session.add(device)
    await session.flush()

    invitation.used_count += 1
    invitation.used_at = datetime.now(timezone.utc)
    if invitation.used_count >= invitation.max_uses:
        invitation.status = InvitationStatus.ACCEPTED

    grant = AccessGrant(
        grant_type=GrantType.INVITATION,
        scope=invitation.scope or "device",
        permissions=invitation.permissions,
        actor=payload.get("name", "device"),
        approver_id=invitation.created_by,
        status="active",
        expires_at=invitation.expires_at,
    )
    session.add(grant)

    await record_audit(
        session,
        action="device.register",
        resource="devices",
        detail={"device_name": device.name, "grant_id": str(grant.id)},
        ip_address=request.client.host if request.client else None,
    )
    await session.commit()
    await session.refresh(device)

    return {
        "id": str(device.id),
        "name": device.name,
        "token": raw_token,
        "expires_at": device.expires_at.isoformat() if device.expires_at else None,
        "permissions": device.permissions,
    }


@router.get("/status")
async def device_status(
    device: DeviceToken = Depends(get_device),
) -> dict:
    """Return the status of the authenticated device."""
    return {
        "id": str(device.id),
        "name": device.name,
        "is_active": device.is_active,
        "permissions": device.permissions,
        "access_level": device.access_level,
        "last_seen_at": device.last_seen_at.isoformat() if device.last_seen_at else None,
        "expires_at": device.expires_at.isoformat() if device.expires_at else None,
        "note": device.note,
    }


@router.post("/ping")
async def device_ping(
    device: DeviceToken = Depends(get_device),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Update the device's last-seen timestamp (heartbeat)."""
    device.last_seen_at = datetime.now(timezone.utc)
    await session.commit()
    return {"status": "ok", "server_time": device.last_seen_at.isoformat()}


@router.post("/chat")
async def device_chat(
    payload: ChatRequest,
    device: DeviceToken = Depends(get_device),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Send a message to the AI assistant from a device.

    Devices use anonymous mode (public-only AI capabilities) unless they
    have been granted specific permissions.
    """
    from app.services.ai_orchestrator import AIOrchestrator

    orchestrator = AIOrchestrator(session=session)
    response = await orchestrator.chat(
        user=None,
        message=payload.message,
        conversation_id=payload.conversation_id,
    )
    return response


@router.get("/config")
async def device_config(
    device: DeviceToken = Depends(get_device),
) -> dict:
    """Return configuration information useful for the device."""
    return {
        "api_version": "v1",
        "features": {
            "chat": True,
            "web_search": "web.search" in (device.permissions or []),
            "tools": "ai.tools.execute" in (device.permissions or []),
        },
        "limits": {
            "max_input_tokens": 8000,
            "max_output_tokens": 4096,
            "request_timeout_seconds": settings.fetch_timeout_seconds,
        },
    }
