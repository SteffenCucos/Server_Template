from __future__ import annotations

from auth.session.session import Session
from models.base.id import Id

from db.entity_dao import EntityDAO
from db.repository import Repository


class SessionDAO(EntityDAO[Session]):
    def __init__(self, repository: Repository[Session]):
        super().__init__(repository)

    def list_for_user(self, user_id: Id | str) -> list[Session]:
        return [session for session in self.list() if str(session.user_id) == str(user_id)]
