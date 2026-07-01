"""Postgres connection construction helpers."""


def create_postgres_connection(uri: str):
    """Create a psycopg connection for a Postgres database URI."""
    import psycopg

    return psycopg.connect(uri)
