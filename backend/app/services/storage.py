"""File storage abstraction.

Supports local filesystem storage (development) and a future object-storage
provider. Files are never served from a web-root path; downloads go through an
authenticated API endpoint that applies access checks.

Security:
* File type validation via magic bytes, not just extension.
* File size limits enforced server-side.
* Safe, server-generated storage keys (no user-controlled paths).
* Private files require authorization to retrieve.
"""
from __future__ import annotations

import hashlib
import os
import secrets
import shutil
import uuid
from pathlib import Path
from typing import BinaryIO

from app.core.config import settings
from app.core.errors import PermissionDeniedError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Maximum upload size (10 MB by default).
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

# Allowed MIME types for uploads.
ALLOWED_MIME_TYPES = frozenset(
    {
        "application/pdf",
        "text/plain",
        "text/markdown",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
        "audio/mpeg",
        "audio/webm",
        "video/mp4",
    }
)

# File extensions mapped to MIME types for basic extension validation.
_EXTENSION_MIME: dict[str, str] = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".mp3": "audio/mpeg",
    ".webm": "audio/webm",
    ".mp4": "video/mp4",
}

# Magic-byte signatures for content-type verification.
_MAGIC_SIGNATURES: list[tuple[bytes, str]] = [
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"RIFF", "audio/webm"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
    (b"%PDF", "application/pdf"),
    (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "application/msword"),
]


class StoredFile:
    """Metadata about a stored file."""

    def __init__(
        self,
        *,
        filename: str,
        content_type: str,
        size: int,
        storage_key: str,
        path: str,
        checksum: str,
    ) -> None:
        self.filename = filename
        self.content_type = content_type
        self.size = size
        self.storage_key = storage_key
        self.path = path
        self.checksum = checksum


def _storage_root() -> Path:
    """Return the local storage root directory."""
    root = Path(settings.storage_root)
    root.mkdir(parents=True, exist_ok=True)
    return root


def _detect_mime_type(data: bytes) -> str | None:
    """Detect MIME type from file magic bytes."""
    for sig, mime in _MAGIC_SIGNATURES:
        if data.startswith(sig):
            return mime
    # Simple text detection.
    try:
        decoded = data[:1024].decode("utf-8")
        if all(ord(ch) >= 32 or ch in "\n\r\t" for ch in decoded):
            return "text/plain"
    except (UnicodeDecodeError, ValueError):
        pass
    return None


def validate_file_type(filename: str, data: bytes) -> str:
    """Validate file type by extension and magic bytes.

    Returns the detected MIME type.
    Raises ``ValueError`` if the file is not allowed.
    """
    ext = Path(filename).suffix.lower()
    ext_mime = _EXTENSION_MIME.get(ext)

    detected = _detect_mime_type(data)

    if detected is None and ext_mime is None:
        raise ValueError(f"File type not recognized for '{filename}'")

    # Cross-check extension vs. detected type where both are known.
    if detected and ext_mime and detected != ext_mime:
        # Some formats have loose magic bytes; only reject clear mismatches.
        if detected.startswith("text/") and not ext_mime.startswith("text/"):
            raise ValueError(
                f"File content does not match extension '{ext}' "
                f"(detected {detected})"
            )

    mime = detected or ext_mime
    if mime not in ALLOWED_MIME_TYPES:
        raise ValueError(f"File type '{mime}' is not allowed")

    return mime  # type: ignore[return-value]


def generate_storage_key(filename: str) -> str:
    """Generate a safe, unique storage key for a file."""
    ext = Path(filename).suffix.lower()
    safe_name = hashlib.sha256(f"{filename}{uuid.uuid4()}".encode()).hexdigest()[:32]
    return f"{safe_name}{ext}"


def get_content_disposition(filename: str, content_type: str) -> str:
    """Return a safe Content-Disposition header value."""
    safe_name = os.path.basename(filename)
    if not safe_name:
        safe_name = "download"
    if content_type.startswith(("text/", "application/json", "application/xml")):
        return f'inline; filename="{safe_name}"'
    return f'attachment; filename="{safe_name}"'


class LocalStorageBackend:
    """Local filesystem storage backend."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or _storage_root()

    def store(
        self,
        *,
        filename: str,
        data: bytes,
        content_type: str,
    ) -> StoredFile:
        """Store raw file data and return metadata."""
        if len(data) > MAX_UPLOAD_BYTES:
            raise ValueError(
                f"File exceeds maximum size of {MAX_UPLOAD_BYTES} bytes"
            )

        storage_key = generate_storage_key(filename)
        checksum = hashlib.sha256(data).hexdigest()
        # Subdirectory per first two chars of key for reasonable fan-out.
        subdir = self.root / storage_key[:2]
        subdir.mkdir(parents=True, exist_ok=True)
        dest = subdir / storage_key

        if dest.exists():
            # Extremely unlikely; regenerate the key.
            storage_key = generate_storage_key(filename)
            dest = subdir / storage_key

        dest.write_bytes(data)

        relative = dest.relative_to(self.root) if dest.is_relative_to(self.root) else dest
        return StoredFile(
            filename=filename,
            content_type=content_type,
            size=len(data),
            storage_key=storage_key,
            path=str(relative),
            checksum=checksum,
        )

    def retrieve(self, storage_key: str, *, is_public: bool = False) -> tuple[bytes, str]:
        """Retrieve file data by storage key.

        Applies path traversal protection: storage keys are never used as raw
        paths; they are validated to be within the root directory.
        """
        if not storage_key or ".." in storage_key or "/" in storage_key or "\\" in storage_key:
            raise PermissionDeniedError("Invalid storage key")

        # storage_key format is <2-char-hash>/<hash><ext>
        target = self.root / storage_key[:2] / storage_key
        resolved = target.resolve()
        if not str(resolved).startswith(str(self.root.resolve())):
            raise PermissionDeniedError("Access to file denied")
        if not resolved.exists():
            raise FileNotFoundError(f"File not found: {storage_key}")

        data = resolved.read_bytes()
        # Determine content type from extension.
        ext = Path(storage_key).suffix.lower()
        content_type = _EXTENSION_MIME.get(ext, "application/octet-stream")
        return data, content_type

    def delete(self, storage_key: str) -> bool:
        """Delete a file by storage key. Returns True if deleted."""
        if not storage_key or ".." in storage_key or "/" in storage_key or "\\" in storage_key:
            return False
        target = self.root / storage_key[:2] / storage_key
        resolved = target.resolve()
        if not str(resolved).startswith(str(self.root.resolve())):
            return False
        if resolved.exists():
            resolved.unlink()
            return True
        return False

    def cleanup_empty_dirs(self) -> None:
        """Remove empty subdirectories under the root."""
        for child in self.root.iterdir():
            if child.is_dir() and not any(child.iterdir()):
                try:
                    child.rmdir()
                except OSError:
                    pass


# A single shared instance for the process.
_storage: LocalStorageBackend | None = None


def get_storage() -> LocalStorageBackend:
    """Return the process-wide storage backend."""
    global _storage
    if _storage is None:
        _storage = LocalStorageBackend()
    return _storage
