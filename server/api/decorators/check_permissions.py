"""Backward-compatible permission annotation."""

from collections.abc import Callable

from api.auth import requires_permission


def check_permission(permission: str | None = None) -> Callable:
    """Attach permission metadata without constructing persistence objects."""
    if permission is None:
        return lambda endpoint: endpoint
    return requires_permission(permission)
