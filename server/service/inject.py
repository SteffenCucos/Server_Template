
from typing import Callable, Type, TypeVar

from kink import di

T = TypeVar('T')


class Injector():
    
    @staticmethod
    def inject(_type: Type[T]) -> Callable[[], T]:
        return lambda: di[_type]

    @staticmethod
    def get_instance(_type: Type[T]) ->  T:
        return Injector.inject(_type)()
