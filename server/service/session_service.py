import logging

from auth.session.session import Session
from db.repository import Repository
from models.base.id import Id
from models.user.user import User

logger = logging.getLogger(__name__)


class SessionService:
    def __init__(self, session_repository: Repository[Session]):
        self.session_repository = session_repository

    def create_session(self, user: User) -> Session:
        session = Session(user._id)
        return self.session_repository.create(session)

    def get_session(self, session_id: Id) -> Session | None:
        return self.session_repository.get_by_id(str(session_id))

    def get_all(self) -> list[Session]:
        return self.session_repository.list(limit=10000)

    def end_session(self, session_id: Id) -> bool:
        return self.session_repository.delete(str(session_id))

    def end_sessions_for_user(self, user_id: Id) -> None:
        for session in self.get_all():
            if session.user_id == user_id:
                self.end_session(session._id)
