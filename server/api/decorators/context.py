import logging
from typing import Any

from api.decorators.decorator import decorator
from models.request_context import RequestContext
from service.inject import Injector
from service.session_service import SessionService
from service.user_service import UserService
from starlette.requests import Request

logger = logging.getLogger()

def set_context():
    '''Creates a context object for the request containing informations about the callers session and user
    '''
    def set_context_wrapper(request: Request, *positional, **named):
        logger.info("Setting request context")
        # Sets request specific context
        session_service = Injector.get_instance(SessionService)
        user_service = Injector.get_instance(UserService)

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
