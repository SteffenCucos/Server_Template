import logging

from config import config
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
# In memory mongo client
from pymongo_inmemory import MongoClient as MemClient

logger = logging.getLogger()

try:
    client = MongoClient(config.mongo.connection_string, serverSelectionTimeoutMS=100, connectTimeoutMS=20000)
    client.server_info()
    logger.info("Using real mongo client")
except:
    client = MemClient()
    logger.info("Using in memory mongo client")

# Think of how we can build transactions into this
# https://www.mongodb.com/docs/manual/core/transactions/#:~:text=For%20situations%20that%20require%20atomicity,databases%2C%20documents%2C%20and%20shards.


def get_collection(database: str, collectionName: str) -> Collection:
    return get_database(database).get_collection(collectionName)

def get_database(database: str) -> Database:
    return client.get_database(database)
