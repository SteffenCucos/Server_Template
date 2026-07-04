import logging

from api.decorators.decorator import decorator
from api.exceptions import ForbiddenException
from auth.rbac import Permission as PermModel
from auth.rbac import RolePermission, UserRole
from db import DatabaseSettings, PSerializeEntitySerializer, create_repository
from db.rbac_dao import PermDAO, RolePermDAO, UserRoleDAO
from models.request_context import RequestContext
from service.authorization_service import AuthorizationService
from starlette.requests import Request

logger = logging.getLogger()


def check_permission(permission: str = None):
    def check_permission_wrapper(request: Request, *positional, **named):
        request_context = RequestContext.get_context()
        user = request_context.current_user

        if not user:
            logger.info("Access check failed: No user in request context")
            raise ForbiddenException("You don't have access to this resource")

        filled_in = permission.format(**named)
        if permission and not _user_has_access(user._id, filled_in):
            logger.info("Access check failed: No matching RBAC grant")
            raise ForbiddenException("You don't have access to this resource")

    return decorator(pre=check_permission_wrapper)


def _user_has_access(user_id: object, required: str) -> bool:
    settings = DatabaseSettings.from_env()
    user_role_repository = create_repository(
        settings=settings,
        resource_name="user_roles",
        serializer=PSerializeEntitySerializer(UserRole),
        id_field="_id",
    )
    role_perm_repository = create_repository(
        settings=settings,
        resource_name="role_perms",
        serializer=PSerializeEntitySerializer(RolePermission),
        id_field="_id",
    )
    perm_repository = create_repository(
        settings=settings,
        resource_name="perms",
        serializer=PSerializeEntitySerializer(PermModel),
        id_field="_id",
    )

    try:
        service = AuthorizationService(
            UserRoleDAO(user_role_repository),
            RolePermDAO(role_perm_repository),
            PermDAO(perm_repository),
        )
        return service.user_has_access(user_id, required)
    finally:
        user_role_repository.close()
        role_perm_repository.close()
        perm_repository.close()
