"""FastAPI dependencies that enforce route authentication and permissions."""

import logging
from collections.abc import AsyncIterator
from typing import Annotated

from api.exceptions import ForbiddenException, UnauthorizedException
from auth.authorization_service import AuthorizationService
from auth.dependencies import get_authz_service, get_session_service
from auth.session.session_service import SessionService
from fastapi import Depends, Request
from models.request_context import RequestContext
from users.dependencies import get_user_service
from users.user import User
from users.user_service import UserService

from .route_permissions import PermissionRequirement

logger = logging.getLogger(__name__)


async def get_request_context(
    request: Request,
    session_service: Annotated[SessionService, Depends(get_session_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> AsyncIterator[RequestContext]:
    """Build and clean up the caller context inside FastAPI's DI lifecycle."""
    request_context = RequestContext.set_context()
    request_context.filled = True

    session_id = request.cookies.get("session_id")
    request_context.session_id = session_id

    try:
        if session := await session_service.get_session(session_id):
            request_context.session = session
            request_context.current_user_id = session.user_id
            request_context.session_expired = session.is_expired()

            if user := await user_service.get_user(session.user_id):
                request_context.current_user = user

        request.state.request_context = request_context
        yield request_context
    finally:
        RequestContext.remove_context()


def require_current_user(
    request_context: Annotated[RequestContext, Depends(get_request_context)],
) -> User:
    """Return the authenticated user or reject the request with HTTP 401."""
    if not request_context.current_user:
        logger.info("Authentication failed: user does not exist")
        raise UnauthorizedException("You don't have permission to access this resource")

    if not request_context.session:
        logger.info("Authentication failed: session does not exist")
        raise UnauthorizedException("You don't have permission to access this resource")

    if request_context.session_expired:
        logger.info("Authentication failed: session expired")
        raise UnauthorizedException("You don't have permission to access this resource")

    return request_context.current_user


class RequirePermission:
    """Callable dependency bound to one route's permission metadata."""

    def __init__(self, requirement: PermissionRequirement):
        self.requirement = requirement

    async def __call__(
        self,
        request: Request,
        user: Annotated[User, Depends(require_current_user)],
        authorization_service: Annotated[
            AuthorizationService,
            Depends(get_authz_service),
        ],
    ) -> None:
        permission = self._resolve_permission(
            self.requirement.permission,
            request,
        )
        if await authorization_service.user_has_access(user._id, permission):
            return

        logger.info(
            "Authorization failed for user %s: %s",
            user._id,
            permission,
        )
        raise ForbiddenException("You don't have access to this resource")

    @staticmethod
    def _resolve_permission(template: str, request: Request) -> str:
        try:
            return template.format(**request.path_params)
        except KeyError as error:
            missing_parameter = error.args[0]
            raise RuntimeError(
                f"Permission template {template!r} references missing path parameter "
                f"{missing_parameter!r}"
            ) from error
