import logging
from typing import Annotated, Any

from api.decorators.decorator import decorator
from auth.session.session import Session
from db import DatabaseSettings, PSerializeEntitySerializer, create_repository
from db.daos.session_dao import SessionDAO
from db.daos.user_dao import UserDAO
from models.request_context import RequestContext
from models.user.user import User
from server.service.dependencies import get_session_service, get_user_service
from service.session_service import SessionService
from service.user_service import UserService
from starlette.requests import Request
from fastapi import Depends

logger = logging.getLogger()


def set_context():
    """Create a request context containing the caller's session and user."""

    def set_context_wrapper(request: Request, 
                            session_service: Annotated[SessionService, Depends(get_session_service)],
                            user_service: Annotated[UserService, Depends(get_user_service)], *positional, **named):
        logger.info("Setting request context")
        request_context = RequestContext.set_context()
        request_context.filled = True

        session_id = request.cookies.get("session_id")
        request_context.session_id = session_id
        if session := session_service.get_session(session_id):
            request_context.session = session
            request_context.current_user_id = session.user_id
            request_context.session_expired = session.is_expired()
            if user := user_service.get_user(session.user_id):
                request_context.current_user = user

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
