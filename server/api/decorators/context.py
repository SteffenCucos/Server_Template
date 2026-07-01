import logging
from typing import Any

from api.decorators.decorator import decorator
from auth.session.session import Session
from db.connection import DatabaseSettings
from db.pserialize_entity_serializer import PSerializeEntitySerializer
from db.repository_creation import create_repository
from db.session_dao import SessionDAO
from db.user_dao import UserDAO
from models.request_context import RequestContext
from models.user.user import User
from service.session_service import SessionService
from service.user_service import UserService
from starlette.requests import Request

logger = logging.getLogger()


def set_context():
    """Create a request context containing the caller's session and user."""

    def set_context_wrapper(request: Request, *positional, **named):
        logger.info("Setting request context")
        request_context = RequestContext.set_context()
        request_context.filled = True

        settings = DatabaseSettings.from_env()
        session_repository = create_repository(
            settings=settings,
            resource_name="sessions",
            serializer=PSerializeEntitySerializer(Session),
            id_field="_id",
        )
        user_repository = create_repository(
            settings=settings,
            resource_name="users",
            serializer=PSerializeEntitySerializer(User),
            id_field="_id",
        )

        try:
            session_service = SessionService(SessionDAO(session_repository))
            user_service = UserService(UserDAO(user_repository))

            session_id = request.cookies.get("session_id")
            request_context.session_id = session_id
            if session := session_service.get_session(session_id):
                request_context.session = session
                request_context.current_user_id = session.user_id
                request_context.session_expired = session.is_expired()
                if user := user_service.get_user(session.user_id):
                    request_context.current_user = user
        finally:
            session_repository.close()
            user_repository.close()

        if request_context.session:
            logger.info(request_context.session)
        else:
            logger.info("Session: None")

    def unset_context_wrapper(result: Any, exception: Exception | None, request: Request, *positional, **named):
        # We need to reset the context at the end of the request so that the next time
        # a request is served on the same thread, the context isn't already set
        logger.info("Zeroing request context")
        RequestContext.remove_context()

    return decorator(pre=set_context_wrapper, post=unset_context_wrapper)
