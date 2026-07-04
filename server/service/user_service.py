import logging
from dataclasses import dataclass

from api.exceptions import UnprocessableEntityException
from db.user_dao import UserDAO
from models.base.id import Id
from models.user.user import User

logger = logging.getLogger(__name__)


@dataclass
class CreateUserRequest:
    user_name: str
    password: str
    email: str


class UserService:
    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    def create_user(self, user_request: CreateUserRequest) -> User:
        maybe_exists = self.user_dao.get_by_name(user_request.user_name)
        if maybe_exists:
            raise UnprocessableEntityException("Username is already taken")

        maybe_exists = self.user_dao.get_by_email(user_request.email)
        if maybe_exists:
            raise UnprocessableEntityException("Email is already in use.")

        user = User(
            user_name=user_request.user_name,
            password=user_request.password,
            email=user_request.email,
        )
        return self.user_dao.create(user)

    def get_user(self, user_id: Id | str) -> User | None:
        return self.user_dao.get_by_id(user_id)

    def get_user_by_name(self, user_name: str) -> User | None:
        return self.user_dao.get_by_name(user_name)

    def get_all_users(self) -> list[User]:
        return self.user_dao.list(limit=10_000)

    def delete_user(self, user: User) -> bool:
        return self.user_dao.delete(user._id)
