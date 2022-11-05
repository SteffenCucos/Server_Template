from pymongo.collection import Collection
from pymongo.database import Database
from pymongo import MongoClient

# In memory mongo client
from pymongo_inmemory import MongoClient as MemClient

from config import get_config


client = MongoClient(get_config().mongo.connection_string, serverSelectionTimeoutMS=100, connectTimeoutMS=20000)


def get_collection(database: str, collectionName: str) -> Collection:
    return get_database(database).get_collection(collectionName)


def get_database(database: str) -> Database:
    return client.get_database(database)
