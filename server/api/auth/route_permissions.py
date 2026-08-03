"""Metadata-only annotations for route authentication and authorization."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, TypeVar

PermissionMode = Literal["any", "all"]
EndpointT = TypeVar("EndpointT", bound=Callable[..., object])

_AUTH_REQUIRED_ATTRIBUTE = "__server_template_auth_required__"
_PERMISSION_REQUIREMENT_ATTRIBUTE = "__server_template_permission_requirement__"


@dataclass(frozen=True)
class PermissionRequirement:
    permissions: tuple[str, ...]
    mode: PermissionMode


def requires_auth(endpoint: EndpointT) -> EndpointT:
    """Mark an endpoint as requiring an authenticated, non-expired session."""
    setattr(endpoint, _AUTH_REQUIRED_ATTRIBUTE, True)
    return endpoint


def requires_permission(permission: str) -> Callable[[EndpointT], EndpointT]:
    """Require one permission after resolving placeholders from path params."""
    return _requires_permissions((permission,), mode="all")


def requires_any_permission(*permissions: str) -> Callable[[EndpointT], EndpointT]:
    """Allow the request when any declared permission is granted."""
    return _requires_permissions(permissions, mode="any")


def requires_all_permissions(*permissions: str) -> Callable[[EndpointT], EndpointT]:
    """Allow the request only when every declared permission is granted."""
    return _requires_permissions(permissions, mode="all")


def get_auth_required(endpoint: Callable[..., object]) -> bool:
    return bool(getattr(endpoint, _AUTH_REQUIRED_ATTRIBUTE, False))


def get_permission_requirement(
    endpoint: Callable[..., object],
) -> PermissionRequirement | None:
    return getattr(endpoint, _PERMISSION_REQUIREMENT_ATTRIBUTE, None)


def _requires_permissions(
    permissions: tuple[str, ...],
    *,
    mode: PermissionMode,
) -> Callable[[EndpointT], EndpointT]:
    normalized = tuple(permission.strip() for permission in permissions)
    if not normalized or any(not permission for permission in normalized):
        raise ValueError("At least one non-empty permission is required")

    requirement = PermissionRequirement(permissions=normalized, mode=mode)

    def mark_endpoint(endpoint: EndpointT) -> EndpointT:
        setattr(endpoint, _AUTH_REQUIRED_ATTRIBUTE, True)
        setattr(endpoint, _PERMISSION_REQUIREMENT_ATTRIBUTE, requirement)
        return endpoint

    return mark_endpoint
