import psycopg
from pgvector.psycopg import register_vector

from app.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER  
from collections.abc import Generator

def get_db() -> Generator[psycopg.Connection, None, None]:
    connection = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

    register_vector(connection)

    try:
        yield connection
    finally:
        connection.close()