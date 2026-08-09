import logging
from dataclasses import dataclass

from api.exceptions import UnprocessableEntityException
from models.base.id import Id
from users.user import User
from users.user_dao import UserDAO

logger = logging.getLogger(__name__)


@dataclass
class CreateUserRequest:
    user_name: str
    password: str
    email: str


@dataclass
class UpdateUserRequest:
    user_name: str | None = None
    password: str | None = None
    email: str | None = None


class UserService:
    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    async def create_user(self, user_request: CreateUserRequest) -> User:
        if await self.user_dao.get_by_name(user_request.user_name):
            raise UnprocessableEntityException("Username is already taken")

        if await self.user_dao.get_by_email(user_request.email):
            raise UnprocessableEntityException("Email is already in use.")

        user = User(
            user_name=user_request.user_name,
            password=user_request.password,
            email=user_request.email,
        )
        return await self.user_dao.create(user)

    async def get_user(self, user_id: Id | str) -> User | None:
        return await self.user_dao.get_by_id(user_id)

    async def get_user_by_name(self, user_name: str) -> User | None:
        return await self.user_dao.get_by_name(user_name)

    async def get_all_users(self) -> list[User]:
        return await self.user_dao.list()

    async def update_user(self, user: User, user_request: UpdateUserRequest) -> User:
        changes: dict[str, str] = {}

        if user_request.user_name is not None and user_request.user_name != user.user_name:
            existing_user = await self.user_dao.get_by_name(user_request.user_name)
            if existing_user and existing_user._id != user._id:
                raise UnprocessableEntityException("Username is already taken")
            changes["user_name"] = user_request.user_name

        if user_request.email is not None and user_request.email != user.email:
            existing_user = await self.user_dao.get_by_email(user_request.email)
            if existing_user and existing_user._id != user._id:
                raise UnprocessableEntityException("Email is already in use.")
            changes["email"] = user_request.email

        if user_request.password is not None and user_request.password != user.password:
            changes["password"] = user_request.password

        if not changes:
            return user

        updated_user = await self.user_dao.update(user._id, changes)
        return updated_user or user

    async def delete_user(self, user: User) -> bool:
        return await self.user_dao.delete(user._id)
