from collections.abc import Callable
import logging
from functools import wraps
from inspect import iscoroutinefunction, signature
from typing import Awaitable

from api.auth.route import AuthzRoute
from db.serializing_middleware import get_application_serializer
from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse, JSONResponse

serializer = get_application_serializer()

logger = logging.getLogger()


class Router(APIRouter):
    '''
    Custom router that runs simpler serialization logic to avoid certain
    pitfalls of FastAPIs standard serialization scheme. The specific use
    cases for us is that FastAPI doesn't support the case where a dataclass
    extends a non dataclass, and it doesn't support serializing enums.

    AuthzRoute is installed by default so route-level auth annotations are
    converted into FastAPI dependencies during route registration.
    '''

    def __init__(self, *positional, **named) -> None:
        named.setdefault("route_class", AuthzRoute)
        logger.info(f"Initialized router: {named.get('prefix', '')}")
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
    def get_serialize_wrapper(func: Callable[..., Response] | Awaitable[Response]) -> Callable[..., Response] | Awaitable[Response]:
        # Preserve the endpoint execution model. FastAPI runs synchronous route
        # handlers in its thread pool, while async handlers must be awaited on
        # the event loop before their result can be serialized.
        if iscoroutinefunction(func):
            @wraps(
                func,
                assigned=("__module__", "__name__", "__qualname__", "__doc__"),
            )
            async def json_serialize(*positional, **named) -> Response:
                result = await func(*positional, **named)
                return Router._serialize_result(result)
        else:
            @wraps(
                func,
                assigned=("__module__", "__name__", "__qualname__", "__doc__"),
            )
            def json_serialize(*positional, **named) -> Response:
                result = func(*positional, **named)
                return Router._serialize_result(result)

        json_serialize.__signature__ = signature(func)
        return json_serialize

    @staticmethod
    def _serialize_result(result: Response) -> Response:
        if isinstance(result, HTMLResponse):
            return result
        return JSONResponse(content=serializer.serialize(result))
