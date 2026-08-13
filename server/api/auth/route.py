"""Auth-aware FastAPI route class and endpoint typing primitives."""

from __future__ import annotations

from typing import Any

from .endpoint_types import EndpointDecorator, EndpointT

from fastapi import Depends
from fastapi.routing import APIRoute

from .dependencies import RequirePermission, require_current_user
from .route_permissions import get_auth_required, get_permission_requirement


class AuthzRoute(APIRoute):
    """Attach authorization dependencies based on endpoint metadata."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        endpoint = self._get_endpoint(args, kwargs)
        dependencies = list(kwargs.pop("dependencies", None) or ())

        permission_requirement = get_permission_requirement(endpoint)
        if permission_requirement and not self._has_permission_dependency(dependencies):
            dependencies.append(Depends(RequirePermission(permission_requirement)))
        elif get_auth_required(endpoint) and not self._has_auth_dependency(dependencies):
            dependencies.append(Depends(require_current_user))

        kwargs["dependencies"] = dependencies
        super().__init__(*args, **kwargs)

    @staticmethod
    def _get_endpoint(
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> EndpointT:
        endpoint = kwargs.get("endpoint")
        if endpoint is None and len(args) > 1:
            endpoint = args[1]
        if not callable(endpoint):
            raise TypeError("AuthzRoute requires a callable endpoint")
        return endpoint

    @staticmethod
    def _has_permission_dependency(dependencies: list[Any]) -> bool:
        return any(
            isinstance(getattr(dependency, "dependency", None), RequirePermission)
            for dependency in dependencies
        )

    @staticmethod
    def _has_auth_dependency(dependencies: list[Any]) -> bool:
        return any(
            getattr(dependency, "dependency", None) is require_current_user
            or isinstance(getattr(dependency, "dependency", None), RequirePermission)
            for dependency in dependencies
        )
