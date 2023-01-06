import logging

from db.serializing_middleware import get_application_serializer
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.requests import Request

from api.decorators.context import set_context
from api.decorators.decorator import apply_func, fix_signature

serializer = get_application_serializer()

logger = logging.getLogger()


class Router(APIRouter):
    '''
    Custom router that runs simpler serialization logic to avoid certain
    pitfalls of FastAPIs standard serialization scheme. The specific use
    cases for us is that FastAPI doesn't support the case where a dataclass
    extends a non dataclass, and it doesn't support serializing enums.
    '''

    def __init__(self, *positional, **named):
        logger.info(f"Initialized router: {named['prefix']}")
        super().__init__(*positional, **named)

    def get(self, endpoint: str):
        def get_decorator(func):    
            return super(Router, self).get(endpoint)(Router.get_serialize_wrapper(func))

        return get_decorator

    def post(self, endpoint: str):
        def post_decorator(func):
            return super(Router, self).post(endpoint)(Router.get_serialize_wrapper(func))

        return post_decorator

    def put(self, endpoint: str):
        def put_decorator(func):
            return super(Router, self).put(endpoint)(Router.get_serialize_wrapper(func))

        return put_decorator

    def delete(self, endpoint: str):
        def delete_decorator(func):
            return super(Router, self).delete(endpoint)(Router.get_serialize_wrapper(func))

        return delete_decorator

    def patch(self, endpoint: str):
        def patch_decorator(func):
            return super(Router, self).patch(endpoint)(Router.get_serialize_wrapper(func))

        return patch_decorator

    @staticmethod
    def get_serialize_wrapper(func):
        @set_context() # Hack to have all routes set context
        # We need to take a request param here to match what other decorators
        # will provide
        def json_serialize(request: Request, *positional, **named):
            result = apply_func(func, request, *positional, **named)

            if isinstance(result, HTMLResponse):
                return result

            return JSONResponse(content=serializer.serialize(result))

        fix_signature(json_serialize, func)

        return json_serialize

   
