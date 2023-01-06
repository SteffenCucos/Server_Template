from __future__ import annotations

import threading
from dataclasses import dataclass

from auth.session.session import Session
from service.threading_utils import get_current_pid

from models.base.id import Id
from models.user.user import User

context_map: dict[str, RequestContext] = {}

@dataclass
class RequestContext():
    session_id: Id = None
    session: Session = None
    session_expired: bool = None
    current_user_id: Id = None
    current_user: User = None
    filled: bool = None

    def __getattr__(self, name):
        return self.__dict__.get(name, None)

    @staticmethod
    def set_context():
        context = RequestContext()
        context_map[get_current_pid()] = context
        return context

    @staticmethod
    def get_context():
        return context_map.get(get_current_pid(), RequestContext())

    @staticmethod
    def remove_context():
        pid = get_current_pid()
        if pid in context_map:
            del context_map[pid]
