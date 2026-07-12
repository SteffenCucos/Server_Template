import logging

from auth.session.session import Session
from db.daos.session_dao import SessionDAO
from models.base.id import Id
from models.user.user import User

logger = logging.getLogger(__name__)


class SessionService:
    def __init__(self, dao: SessionDAO):
        self.dao = dao

    def create_session(self, user: User) -> Session:
        session = Session(user._id)
        return self.dao.create(session)

    def get_session(self, session_id: Id | str) -> Session | None:
        return self.dao.get_by_id(session_id)

    def get_all(self) -> list[Session]:
        return self.dao.list(limit=10_000)

    def end_session(self, session_id: Id | str) -> bool:
        return self.dao.delete(session_id)

    def end_sessions_for_user(self, user_id: Id | str) -> None:
        for session in self.dao.list_for_user(user_id):
            self.end_session(session._id)
