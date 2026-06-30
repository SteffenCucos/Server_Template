"""FastAPI dependency providers for application services."""

from db.dependencies import SessionRepository, UserRepository

from .session_service import SessionService
from .user_service import UserService


def get_user_service(user_repository: UserRepository) -> UserService:
    return UserService(user_repository)


def get_session_service(session_repository: SessionRepository) -> SessionService:
    return SessionService(session_repository)
