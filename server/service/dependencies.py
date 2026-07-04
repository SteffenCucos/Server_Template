"""FastAPI dependency providers for application services."""

from typing import Annotated

from db.dependencies import (
    get_perm_dao,
    get_role_perm_dao,
    get_session_dao,
    get_user_dao,
    get_user_role_dao,
)
from db.rbac_dao import PermDAO, RolePermDAO, UserRoleDAO
from db.session_dao import SessionDAO
from db.user_dao import UserDAO
from fastapi import Depends

from .authorization_service import AuthorizationService
from .session_service import SessionService
from .user_service import UserService


def get_user_service(user_dao: Annotated[UserDAO, Depends(get_user_dao)]) -> UserService:
    return UserService(user_dao)


def get_session_service(session_dao: Annotated[SessionDAO, Depends(get_session_dao)]) -> SessionService:
    return SessionService(session_dao)


def get_authz_service(
    user_role_dao: Annotated[UserRoleDAO, Depends(get_user_role_dao)],
    role_perm_dao: Annotated[RolePermDAO, Depends(get_role_perm_dao)],
    perm_dao: Annotated[PermDAO, Depends(get_perm_dao)],
) -> AuthorizationService:
    return AuthorizationService(user_role_dao, role_perm_dao, perm_dao)
