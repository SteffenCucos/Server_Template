"""Authentication annotation wired into FastAPI dependency injection."""

from api.auth.route_permissions import mark_auth_required


def authenticated():
    """Mark a route as requiring an authenticated, non-expired session."""
    return mark_auth_required
