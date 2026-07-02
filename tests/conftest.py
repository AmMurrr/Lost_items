from pathlib import Path
from typing import Generator
from datetime import date
import sys

import os

import psycopg
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from pgvector import Vector
from pgvector.psycopg import register_vector


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app
from app.services.embedding import build_embedding


@pytest.fixture(scope="session")
def db_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url is None:
        raise RuntimeError("Переменная окружения DATABASE_URL не найдена")
    return database_url


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def sample_item(db_url: str) -> Generator[dict[str, object], None, None]:
    inserted_item_id: int | None = None

    with psycopg.connect(db_url) as conn:
        register_vector(conn)

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT item_id, item_description, found_station, found_date
                FROM found_items
                ORDER BY item_id
                LIMIT 1
                """
            )
            row = cur.fetchone()

            if row is None:
                description = "Тестовый рюкзак с зарядным устройством"
                station = "Тестовая"
                found_date = date(2026, 1, 15)
                found_place = "Тестовая платформа"
                photo_path = None

                cur.execute(
                    """
                    INSERT INTO found_items (
                        found_date,
                        found_station,
                        found_place,
                        item_description,
                        photo_path,
                        description_embedding
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING item_id
                    """,
                    (
                        found_date,
                        station,
                        found_place,
                        description,
                        photo_path,
                        Vector(build_embedding(description)),
                    ),
                )
                inserted_item_id = cur.fetchone()[0]
                conn.commit()

                item = {
                    "id": inserted_item_id,
                    "description": description,
                    "station": station,
                    "found_date": found_date,
                }
            else:
                item = {
                    "id": row[0],
                    "description": row[1],
                    "station": row[2],
                    "found_date": row[3],
                }

    yield item

    if inserted_item_id is not None:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM found_items WHERE item_id = %s", (inserted_item_id,))
            conn.commit()