"""Role-based access control rules.

Maps a user's role to the set of ``AccessLevel`` values they may read, and
exposes helpers used by the tool layer to decide whether a private college
record may be surfaced.
"""
from __future__ import annotations

from app.models.enums import AccessLevel, RoleName

# Ordered from least to most sensitive.
_ALL = frozenset(AccessLevel)

_READ_ACCESS: dict[str, frozenset[AccessLevel]] = {
    RoleName.ADMIN.value: _ALL,
    RoleName.FACULTY.value: frozenset(
        {AccessLevel.PUBLIC, AccessLevel.INTERNAL, AccessLevel.RESTRICTED}
    ),
    RoleName.IDEALAB_MEMBER.value: frozenset(
        {AccessLevel.PUBLIC, AccessLevel.INTERNAL, AccessLevel.RESTRICTED}
    ),
    RoleName.STAFF.value: frozenset({AccessLevel.PUBLIC, AccessLevel.INTERNAL}),
    RoleName.STUDENT.value: frozenset({AccessLevel.PUBLIC, AccessLevel.INTERNAL}),
}

# Anonymous / unauthenticated callers may only ever see public data.
_ANON_ACCESS = frozenset({AccessLevel.PUBLIC})


def allowed_access_levels(role_name: str | None) -> frozenset[AccessLevel]:
    """Return the access levels readable by the given role."""
    if not role_name:
        return _ANON_ACCESS
    return _READ_ACCESS.get(role_name, _ANON_ACCESS)


def can_read(role_name: str | None, level: AccessLevel, *, is_superuser: bool = False) -> bool:
    """Return whether a role may read a record at the given access level."""
    if is_superuser:
        return True
    return level in allowed_access_levels(role_name)


def readable_levels(role_name: str | None, *, is_superuser: bool = False) -> frozenset[AccessLevel]:
    """Access levels a caller may read (used to filter queries)."""
    if is_superuser:
        return _ALL
    return allowed_access_levels(role_name)
