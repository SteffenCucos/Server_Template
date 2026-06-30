"""Database abstraction layer.

The public repository and DAO contracts are intentionally backend-neutral.
Application code should import interfaces from this package and let concrete
repository implementations own Mongo/Postgres connection details.
"""

from .config import DatabaseBackend, DatabaseSettings
from .database import Database, DatabaseUpdate, IdValue
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
    "Repository",
    "create_repository",
]
