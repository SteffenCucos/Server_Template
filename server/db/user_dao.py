


from fastapi import Depends
from kink import inject
from models.user.user import User
from pymongo.collection import Collection

from db.entity_dao import EntityDAO
from db.mongodb import get_collection


def get_users_collection() -> Collection:
    return get_collection("server", "users")


@inject
class UserDAO(EntityDAO[User]):
    def __init__(self, user_collection: Collection = get_collection("server", "users")):
        super().__init__(user_collection, User)
    