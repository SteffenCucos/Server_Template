"""Permission annotation wired into FastAPI dependency injection."""

from api.auth.endpoint_types import EndpointDecorator
from api.auth.route_permissions import mark_permission_required


def check_permission(permission: str | None = None) -> EndpointDecorator:
    """Mark a route as requiring one permission template."""
    if not permission:
        raise ValueError("A non-empty permission is required")
    return mark_permission_required(permission)
