"""Shared typing primitives for auth-aware endpoint decorators and routes."""

from collections.abc import Callable, Awaitable
from typing import Protocol, TypeVar

from fastapi import Response


EndpointT = TypeVar("EndpointT", bound=Callable[..., Response] | Awaitable[Response])


class EndpointDecorator(Protocol):
    def __call__(self, endpoint: EndpointT, /) -> EndpointT:
        ...
