
import inspect
import logging
from typing import Any

from fastapi import Request

logger = logging.getLogger()

def test_print(num: int):
    def test_print_pre(request: Request, *positional, **named):
        print("pre:", num)

    def test_print_post(result: Any, exception: Exception | None, request: Request, *positional, **named):
        print("post:", num)

    return decorator(pre=test_print_pre, post=test_print_post)

def decorator(pre=None, transform=None, post=None):
    def decorator_wrapper(func): # Take the function we're decorating
        def func_replace(request: Request, *positional, **named): # Match the signature
            if pre: # Run pre request logic
                pre(request, *positional, **named)

            exception = None
            result = None
            try:
                result = apply_func(func, request, *positional, **named)
                if transform:
                    result = transform(result)
            except Exception as e:
                exception = e
            
            if post: # Run post request logic
                try:
                    post(result, exception, request, *positional, **named)
                except Exception as e:
                    logger.error("Exception in post func logic", e)
                    pass

            if exception:
                raise exception
            return result

        # Dynamically modify the func_replace signature to match 
        # the actual runtime signature of func
        fix_signature(func_replace, func)
        return func_replace

    return decorator_wrapper

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

    seen = set()
    deduped_params = []
    for param in params:
        if param not in seen:
            deduped_params.append(param)
            seen.add(param)
    

    wrapper.__signature__ = inspect.Signature(
        parameters=deduped_params,
        return_annotation=inspect.signature(func).return_annotation,
    )

def apply_func(func, request: Request, *positional, **named):
    if takes_request(func):
        return func(request, *positional, **named)
    else:
        return func(*positional, **named)

def takes_request(func) -> bool:
    return inspect.signature(func).parameters.__contains__("request")
