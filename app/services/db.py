import psycopg
from pgvector.psycopg import register_vector

from app.config import DATABASE_URL
from collections.abc import Generator


def get_db() -> Generator[psycopg.Connection, None, None]:
    connection = psycopg.connect(DATABASE_URL)

    register_vector(connection)

    try:
        yield connection
    finally:
        connection.close()
