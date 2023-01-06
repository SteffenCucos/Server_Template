


from auth.session.session import Session
from fastapi import Depends
from kink import di, inject
from pymongo.collection import Collection

from db.entity_dao import EntityDAO
from db.mongodb import get_collection


@inject
class SessionDAO(EntityDAO[Session]):
    def __init__(self, session_collection: Collection = get_collection("server", "sessions")):
        super().__init__(session_collection, Session)
    