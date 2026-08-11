"""FastAPI dependency providers for auth domain services."""

from __future__ import annotations

from typing import Annotated

from auth.rbac import Permission as PermModel
from auth.rbac import Role, RolePermission, UserRole
from fastapi import Depends

from db.dependencies import repository_dependency
from db.pserialize_entity_serializer import PSerializeEntitySerializer
from db.repository import Repository

from .rbac.daos import PermDAO, RoleDAO, RolePermDAO, UserRoleDAO
from .session.session import Session
from .session.session_dao import SessionDAO
from .session.session_service import SessionService
from .authorization_service import AuthorizationService
from .authentication_service import AuthenticationService
from .password.dependencies import get_password_service
from .password.password_service import PasswordService
from users.dependencies import get_user_service
from users.user_service import UserService


get_perm_repository = repository_dependency(
    resource_name="perms",
    serializer=PSerializeEntitySerializer(PermModel),
)


get_role_repository = repository_dependency(
    resource_name="roles",
    serializer=PSerializeEntitySerializer(Role),
)


get_user_role_repository = repository_dependency(
    resource_name="user_roles",
    serializer=PSerializeEntitySerializer(UserRole),
)


get_role_perm_repository = repository_dependency(
    resource_name="role_perms",
    serializer=PSerializeEntitySerializer(RolePermission),
)


get_session_repository = repository_dependency(
    resource_name="sessions",
    serializer=PSerializeEntitySerializer(Session),
)


def get_perm_dao(
    repository: Annotated[Repository[PermModel], Depends(get_perm_repository)],
) -> PermDAO:
    return PermDAO(repository)


def get_role_dao(
    repository: Annotated[Repository[Role], Depends(get_role_repository)],
) -> RoleDAO:
    return RoleDAO(repository)


def get_user_role_dao(
    repository: Annotated[Repository[UserRole], Depends(get_user_role_repository)],
) -> UserRoleDAO:
    return UserRoleDAO(repository)


def get_role_perm_dao(
    repository: Annotated[Repository[RolePermission], Depends(get_role_perm_repository)],
) -> RolePermDAO:
    return RolePermDAO(repository)


def get_session_dao(
    repository: Annotated[Repository[Session], Depends(get_session_repository)],
) -> SessionDAO:
    return SessionDAO(repository)


def get_session_service(session_dao: Annotated[SessionDAO, Depends(get_session_dao)]) -> SessionService:
    return SessionService(session_dao)


def get_authentication_service(
    user_service: Annotated[UserService, Depends(get_user_service)],
    password_service: Annotated[PasswordService, Depends(get_password_service)],
    session_service: Annotated[SessionService, Depends(get_session_service)],
) -> AuthenticationService:
    return AuthenticationService(user_service, password_service, session_service)


def get_authorization_service(
    user_role_dao: Annotated[UserRoleDAO, Depends(get_user_role_dao)],
    role_perm_dao: Annotated[RolePermDAO, Depends(get_role_perm_dao)],
    perm_dao: Annotated[PermDAO, Depends(get_perm_dao)],
) -> AuthorizationService:
    return AuthorizationService(user_role_dao, role_perm_dao, perm_dao)
