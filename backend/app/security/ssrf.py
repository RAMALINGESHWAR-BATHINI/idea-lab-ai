"""SSRF protection for outbound URL fetching.

Only public HTTP(S) URLs are permitted. The guard rejects non-HTTP schemes,
embedded credentials, and any host resolving to a private, loopback,
link-local, multicast, reserved or unspecified address (which also blocks
cloud metadata endpoints such as 169.254.169.254).
"""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlsplit, urlunsplit

from app.core.config import settings
from app.core.errors import UnsafeURLError
from app.core.logging import get_logger

logger = get_logger(__name__)

_ALLOWED_SCHEMES = {"http", "https"}
_BLOCKED_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "ip6-localhost",
    "metadata.google.internal",
    "metadata",
}


def _is_blocked_ip(ip: ipaddress._BaseAddress) -> bool:
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _resolve(hostname: str) -> list[str]:
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise UnsafeURLError(f"Could not resolve host: {hostname}") from exc
    addresses: list[str] = []
    for info in infos:
        sockaddr = info[4]
        if sockaddr and sockaddr[0]:
            addresses.append(sockaddr[0])
    return addresses


def validate_public_url(url: str) -> str:
    """Validate a URL and return a normalised form.

    Raises ``UnsafeURLError`` if the URL is not safe to fetch.
    """
    if not url or not isinstance(url, str):
        raise UnsafeURLError("A non-empty URL is required")

    url = url.strip()
    if "://" not in url:
        url = "https://" + url

    parts = urlsplit(url)

    if parts.scheme.lower() not in _ALLOWED_SCHEMES:
        raise UnsafeURLError(f"Unsupported URL scheme: {parts.scheme!r}")

    if parts.username or parts.password:
        raise UnsafeURLError("URLs with embedded credentials are not allowed")

    hostname = parts.hostname
    if not hostname:
        raise UnsafeURLError("URL is missing a host")

    if hostname.lower() in _BLOCKED_HOSTNAMES:
        raise UnsafeURLError(f"Host is not allowed: {hostname}")

    # If the host is a literal IP, check it directly; otherwise resolve it.
    if not settings.ssrf_allow_private_hosts:
        try:
            literal = ipaddress.ip_address(hostname)
            if _is_blocked_ip(literal):
                raise UnsafeURLError("Refusing to fetch a non-public address")
        except ValueError:
            for address in _resolve(hostname):
                try:
                    ip = ipaddress.ip_address(address)
                except ValueError:
                    continue
                if _is_blocked_ip(ip):
                    logger.warning(
                        "ssrf_blocked", host=hostname, resolved=address
                    )
                    raise UnsafeURLError(
                        "Refusing to fetch a host that resolves to a non-public address"
                    )

    # Rebuild without credentials/params normalisation surprises.
    netloc = hostname
    if parts.port:
        netloc = f"{hostname}:{parts.port}"
    return urlunsplit((parts.scheme.lower(), netloc, parts.path or "/", parts.query, ""))
