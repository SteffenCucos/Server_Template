import inspect

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from starlette.requests import Request

from db.serializing_middleware import get_application_serializer
serializer = get_application_serializer()


class Router(APIRouter):
    '''
    Custom router that runs simpler serialization logic to avoid certain
    pitfalls of FastAPIs standard serialization scheme. The specific use
    cases for us is that FastAPI doesn't support the case where a dataclass
    extends a non dataclass, and it doesn't support serializing enums.
    '''

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
    def fix_signature(wrapper, func):
        params = [
            # Skip *args and **kwargs from wrapper parameters:
            *filter(
                lambda p: p.kind not in (
                    inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD),
                inspect.signature(wrapper).parameters.values()
            ),
            # Use all parameters from handler
            *inspect.signature(func).parameters.values()
        ]

        wrapper.__signature__ = inspect.Signature(
            parameters=params,
            return_annotation=inspect.signature(func).return_annotation,
        )

    @staticmethod
    def get_serialize_wrapper(func):
        def json_serialize(request: Request, *positional, **named):
            result = func(*positional, **named)
            return JSONResponse(content=serializer.serialize(result))

        Router.fix_signature(json_serialize, func)

        return json_serialize
