
import logging

from auth.session.session import Session
from db.session_dao import SessionDAO
from kink import inject
from models.base.id import Id
from models.user.user import User

logger = logging.getLogger(__name__)

@inject
class SessionService():
    def __init__(self, 
        session_dao: SessionDAO
    ):
        self.session_dao = session_dao

    def create_session(self, user: User) -> Session:
        session = Session(user._id)
        id = self.session_dao.save(session)
        return session

    def get_session(self, session_id: Id) -> Session | None:
        return self.session_dao.find_one_by_id(session_id)

    def get_all(self) -> list[Session]:
        return self.session_dao.find_all()

    def end_session(self, session_id: Id):
        self.session_dao.delete_by_id(session_id)

    def end_sessions_for_user(self, user_id: Id):
        sessions = [*filter(
            lambda session: session.user_id == user_id,
            self.get_all()
        )]

        for session in sessions:
            self.end_session(session._id)

