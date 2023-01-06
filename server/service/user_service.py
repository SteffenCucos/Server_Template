
import logging
from dataclasses import dataclass

from api.exceptions import UnprocessableEntityException
from db.user_dao import UserDAO
from models.base.id import Id
from models.user.user import User

logger = logging.getLogger(__name__)

from kink import inject


@dataclass
class CreateUserRequest:
    user_name: str
    password: str
    email: str


@inject
class UserService():
    def __init__(self,
        user_dao: UserDAO
    ):
        self.user_dao = user_dao

    def create_user(self, user_request: CreateUserRequest) -> User:
        maybe_exists = self.user_dao.find_one_by_condition({"user_name": user_request.user_name})
        if maybe_exists:
            raise UnprocessableEntityException("Username is already taken")

        maybe_exists = self.user_dao.find_one_by_condition({"email": user_request.email})
        if maybe_exists:
            raise UnprocessableEntityException("Email is already in use.")

        user = User(
            user_name=user_request.user_name,
            password=user_request.password,
            email=user_request.email
        )

        user.permissions = [
            f"read/users/{user._id}",
            f"update/users/{user._id}",
            f"delete/users/{user._id}"
        ]

        save_id = self.user_dao.save(user)
        assert user._id._id == save_id
        return user


    def get_user(self, user_id: Id) -> User | None:
        return self.user_dao.find_one_by_id(user_id)

    def get_user_by_name(self, user_name: str) -> User | None:
        return self.user_dao.find_one_by_condition({'user_name': user_name})

    def get_all_users(self) -> list[User]:
        return self.user_dao.find_all()
    
    def delete_user(self, user: User):
        return self.user_dao.delete_by_id(user._id)
