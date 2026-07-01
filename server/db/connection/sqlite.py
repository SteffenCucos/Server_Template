"""SQLite connection construction helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from urllib.parse import urlparse

_MEMORY_SQLITE_URIS = {":memory:", "sqlite:///:memory:"}
_SHARED_MEMORY_CONNECTIONS: dict[str, sqlite3.Connection] = {}


def create_sqlite_connection(uri: str) -> tuple[sqlite3.Connection, bool]:
    """Create a SQLite connection and report whether the caller owns it."""
    if uri in _MEMORY_SQLITE_URIS:
        if uri not in _SHARED_MEMORY_CONNECTIONS:
            _SHARED_MEMORY_CONNECTIONS[uri] = sqlite3.connect(":memory:", check_same_thread=False)
        return _SHARED_MEMORY_CONNECTIONS[uri], False

    return sqlite3.connect(sqlite_path_from_uri(uri), check_same_thread=False), True


def sqlite_path_from_uri(uri: str) -> str:
    """Translate a sqlite:// URI into a local filesystem path."""
    parsed = urlparse(uri)
    if parsed.scheme != "sqlite":
        return uri

    path = parsed.path
    if path.startswith("/") and not path.startswith("//"):
        path = path[1:]

    db_path = Path(path)
    if db_path.parent != Path(""):
        db_path.parent.mkdir(parents=True, exist_ok=True)
    return str(db_path)
