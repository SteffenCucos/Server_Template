"""FastAPI authorization metadata and dependency wiring."""

from .route_permissions import (
    PermissionRequirement,
    get_auth_required,
    get_permission_requirement,
    requires_all_permissions,
    requires_any_permission,
    requires_auth,
    requires_permission,
)

__all__ = [
    "PermissionRequirement",
    "get_auth_required",
    "get_permission_requirement",
    "requires_all_permissions",
    "requires_any_permission",
    "requires_auth",
    "requires_permission",
]
