"""Database abstraction layer.

Application code should depend on entity DAOs and repository interfaces while
concrete repository implementations own Mongo/Postgres/SQLite connection details.
"""

from .config import DatabaseBackend, DatabaseSettings
from .dependencies import (
    SessionDAODep,
    SessionRepository,
    UserDAODep,
    UserRepository,
    get_database_settings,
    get_session_dao,
    get_session_repository,
    get_user_dao,
    get_user_repository,
    repository_dependency,
)
from .entity_dao import EntityDAO
from .factory import create_repository
from .pserialize_entity_serializer import PSerializeEntitySerializer
from .repository import EntitySerializer, MappingSerializer, Repository
from .session_dao import SessionDAO
from .user_dao import UserDAO

__all__ = [
    "DatabaseBackend",
    "DatabaseSettings",
    "EntityDAO",
    "EntitySerializer",
    "MappingSerializer",
    "PSerializeEntitySerializer",
    "Repository",
    "SessionDAO",
    "SessionDAODep",
    "SessionRepository",
    "UserDAO",
    "UserDAODep",
    "UserRepository",
    "create_repository",
    "get_database_settings",
    "get_session_dao",
    "get_session_repository",
    "get_user_dao",
    "get_user_repository",
    "repository_dependency",
]
