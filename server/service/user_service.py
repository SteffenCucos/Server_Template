import logging
from dataclasses import dataclass

from api.exceptions import UnprocessableEntityException
from db.repository import Repository
from models.base.id import Id
from models.user.user import User

logger = logging.getLogger(__name__)


@dataclass
class CreateUserRequest:
    user_name: str
    password: str
    email: str


class UserService:
    def __init__(self, user_repository: Repository[User]):
        self.user_repository = user_repository

    def create_user(self, user_request: CreateUserRequest) -> User:
        maybe_exists = self.user_repository.find_one({"user_name": user_request.user_name})
        if maybe_exists:
            raise UnprocessableEntityException("Username is already taken")

        maybe_exists = self.user_repository.find_one({"email": user_request.email})
        if maybe_exists:
            raise UnprocessableEntityException("Email is already in use.")

        user = User(
            user_name=user_request.user_name,
            password=user_request.password,
            email=user_request.email,
        )

        user.permissions = [
            f"read/users/{user._id}",
            f"update/users/{user._id}",
            f"delete/users/{user._id}",
        ]

        return self.user_repository.create(user)

    def get_user(self, user_id: Id) -> User | None:
        return self.user_repository.get_by_id(str(user_id))

    def get_user_by_name(self, user_name: str) -> User | None:
        return self.user_repository.find_one({"user_name": user_name})

    def get_all_users(self) -> list[User]:
        return self.user_repository.list(limit=10_000)

    def delete_user(self, user: User) -> bool:
        return self.user_repository.delete(str(user._id))
