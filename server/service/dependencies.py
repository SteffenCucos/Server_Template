"""FastAPI dependency providers for application services."""

from db.dependencies import SessionDAODep, UserDAODep

from .session_service import SessionService
from .user_service import UserService


def get_user_service(user_dao: UserDAODep) -> UserService:
    return UserService(user_dao)


def get_session_service(session_dao: SessionDAODep) -> SessionService:
    return SessionService(session_dao)
