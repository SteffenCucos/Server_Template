"""Permission annotation wired into FastAPI dependency injection."""

from collections.abc import Callable

from api.auth.route_permissions import mark_permission_required


def check_permission(permission: str | None = None) -> Callable:
    """Mark a route as requiring one permission template."""
    if permission is None:
        return lambda endpoint: endpoint
    return mark_permission_required(permission)
