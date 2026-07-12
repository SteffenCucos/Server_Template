"""Database abstraction layer."""

from .config import DatabaseBackend, DatabaseSettings
from .dependencies import (
    get_database_settings,
    get_perm_dao,
    get_role_dao,
    get_role_perm_dao,
    get_session_dao,
    get_session_repository,
    get_user_dao,
    get_user_repository,
    get_user_role_dao,
    repository_dependency,
)
from .daos.entity_dao import EntityDAO
from .repository.factory import create_repository
from .pserialize_entity_serializer import PSerializeEntitySerializer
from .daos.rbac import PermDAO, RoleDAO, RolePermDAO, UserRoleDAO
from .repository import EntitySerializer, MappingSerializer, Repository
from .daos.session_dao import SessionDAO
from .daos.user_dao import UserDAO
