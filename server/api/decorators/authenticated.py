import logging

from api.decorators.decorator import decorator
from api.exceptions import UnauthorizedException
from models.request_context import RequestContext
from starlette.requests import Request

logger = logging.getLogger()

def authenticated():
    '''Ensures the caller has a valid session.

    Raises: 
        api.exceptions.UnauthorizedException: If the caller can't be authenticated.
    '''
    def authenticate_user(request: Request, *positional, **named):
        request_context = RequestContext.get_context()

        if not request_context.current_user:
            logger.info("Permission check failed: User does not exist")
            raise UnauthorizedException("You don't have permission to access this resource")

        if not request_context.session:
            logger.info("Permission check failed: Session DNE")
            raise UnauthorizedException("You don't have permission to access this resource")
        
        if request_context.session_expired:
            logger.info("Permission check failed: Session expired")
            raise UnauthorizedException("You don't have permission to access this resource")
        
    return decorator(pre=authenticate_user)
