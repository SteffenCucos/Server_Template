"""Backward-compatible authentication annotation."""

from api.auth import requires_auth


def authenticated():
    """Mark a route as authenticated using the FastAPI DI auth flow."""
    return requires_auth
