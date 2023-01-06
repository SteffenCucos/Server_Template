import logging

from api.decorators.decorator import decorator
from api.exceptions import ForbiddenException
from models.request_context import RequestContext
from starlette.requests import Request

logger = logging.getLogger()

def check_permission(permission: str=None):
    def check_permission_wrapper(request: Request, *positional, **named):
        request_context = RequestContext.get_context()
        user =  request_context.current_user

        if not user:
            logger.info("Permission check failed: No matching permission string")
            raise ForbiddenException("You don't have permission to access this resource")
            
        filled_in = permission.format(**named)
        if permission and not user.has_permission(filled_in):
            logger.info("Permission check failed: No matching permission string")
            raise ForbiddenException("You don't have permission to access this resource")

    return decorator(pre=check_permission_wrapper)
