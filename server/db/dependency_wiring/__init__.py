"""FastAPI dependency wiring for the database layer."""

from .repositories import (
    get_database_settings,
    get_session_dao,
    get_session_repository,
    get_user_dao,
    get_user_repository,
    repository_dependency,
)

__all__ = [
    "get_database_settings",
    "get_session_dao",
    "get_session_repository",
    "get_user_dao",
    "get_user_repository",
    "repository_dependency",
]
