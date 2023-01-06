import logging

from api.decorators.decorator import decorator
from api.exceptions import UnauthorizedException
from models.request_context import RequestContext
from starlette.requests import Request

logger = logging.getLogger()

def authenticated():
    '''
    Handles
    '''
    def authorized_wrapper(request: Request, *positional, **named):
        request_context = RequestContext.get_context()
        session = request_context.session
        session_expired = request_context.session_expired
        user =  request_context.current_user

        if not session:
            logger.info("Permission check failed: Session DNE")
            raise UnauthorizedException("You don't have permission to access this resource")
        
        if session_expired:
            logger.info("Permission check failed: Session expired")
            raise UnauthorizedException("You don't have permission to access this resource")

        if not user:
            logger.info("Permission check failed: User does not exist")
            raise UnauthorizedException("You don't have permission to access this resource")
        
    return decorator(pre=authorized_wrapper)
