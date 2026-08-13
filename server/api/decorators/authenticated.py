"""Authentication annotation wired into FastAPI dependency injection."""

from api.auth.route import EndpointDecorator
from api.auth.route_permissions import mark_auth_required


def authenticated() -> EndpointDecorator:
    """Mark a route as requiring an authenticated, non-expired session."""
    return mark_auth_required
