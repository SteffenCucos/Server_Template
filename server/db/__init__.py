"""Database abstraction layer.

The public repository contract is intentionally backend-neutral. Application code should
import repository interfaces from this package and let concrete backend modules own
Mongo/Postgres connection details.
"""

from .config import DatabaseBackend, DatabaseSettings
from .factory import create_repository
from .repository import EntitySerializer, MappingSerializer, Repository

__all__ = [
    "DatabaseBackend",
    "DatabaseSettings",
    "EntitySerializer",
    "MappingSerializer",
    "Repository",
    "create_repository",
]
