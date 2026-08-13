"""Shared typing primitives for auth-aware endpoint decorators and routes."""

from collections.abc import Callable
from typing import Protocol, TypeVar


EndpointT = TypeVar("EndpointT", bound=Callable[..., object])


class EndpointDecorator(Protocol):
    def __call__(self, endpoint: EndpointT, /) -> EndpointT:
        ...
