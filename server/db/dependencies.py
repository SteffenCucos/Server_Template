"""Compatibility imports for database dependency wiring."""

from db.dependency_wiring import (
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
