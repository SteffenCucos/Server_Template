from __future__ import annotations

import threading
from dataclasses import dataclass

from auth.session.session import Session
from models.base.id import Id
from service.threading_utils import get_current_pid
from users.user import User

context_map: dict[int, RequestContext] = {}

@dataclass
class RequestContext():
    session_id: Id | None = None
    session: Session | None = None
    session_expired: bool | None = None
    current_user_id: Id | None = None
    current_user: User | None = None
    filled: bool | None = None

    def __getattr__(self, name: str) -> object | None:
        return self.__dict__.get(name, None)

    @staticmethod
    def set_context() -> RequestContext:
        context = RequestContext()
        context_map[get_current_pid()] = context
        return context

    @staticmethod
    def get_context() -> RequestContext:
        return context_map.get(get_current_pid(), RequestContext())

    @staticmethod
    def remove_context() -> None:
        pid = get_current_pid()
        if pid in context_map:
            del context_map[pid]
