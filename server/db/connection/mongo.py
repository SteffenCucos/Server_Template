"""Mongo connection construction helpers."""

MEMORY_MONGO_URIS = {"memory://", "mongo://memory", "mongodb://memory", "mongodb://in-memory"}
_SHARED_MEMORY_CLIENTS: dict[str, object] = {}


def create_mongo_client(uri: str):
    """Create a Mongo client and report whether the caller owns its lifecycle."""
    if uri in MEMORY_MONGO_URIS:
        from pymongo_inmemory import MongoClient

        if uri not in _SHARED_MEMORY_CLIENTS:
            _SHARED_MEMORY_CLIENTS[uri] = MongoClient()
        return _SHARED_MEMORY_CLIENTS[uri], False

    from pymongo import MongoClient

    return MongoClient(uri), True
