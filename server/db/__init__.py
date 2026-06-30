"""Database abstraction layer.

The public repository and DAO contracts are intentionally backend-neutral.
Application code should import interfaces from this package and let concrete
repository implementations own Mongo/Postgres connection details.
"""

from .config import DatabaseBackend, DatabaseSettings
from .database import Database, DatabaseUpdate, IdValue
from .dependencies import (
    PSerializeEntitySerializer,
    SessionRepository,
    UserRepository,
    get_database_settings,
    get_session_repository,
    get_user_repository,
    repository_dependency,
)
from .factory import create_repository
from .repository import EntitySerializer, MappingSerializer, Repository

__all__ = [
    "Database",
    "DatabaseBackend",
    "DatabaseSettings",
    "DatabaseUpdate",
    "EntitySerializer",
    "IdValue",
    "MappingSerializer",
    "PSerializeEntitySerializer",
    "Repository",
    "SessionRepository",
    "UserRepository",
    "create_repository",
    "get_database_settings",
    "get_session_repository",
    "get_user_repository",
    "repository_dependency",
]
