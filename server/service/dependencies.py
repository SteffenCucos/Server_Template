"""FastAPI dependency providers for application services."""

from typing import Annotated

from db.dependencies import get_session_dao, get_user_dao
from db.session_dao import SessionDAO
from db.user_dao import UserDAO
from fastapi import Depends

from .session_service import SessionService
from .user_service import UserService


def get_user_service(
    user_dao: Annotated[UserDAO, Depends(get_user_dao)],
) -> UserService:
    return UserService(user_dao)


def get_session_service(
    session_dao: Annotated[SessionDAO, Depends(get_session_dao)],
) -> SessionService:
    return SessionService(session_dao)
