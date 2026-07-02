from datetime import date, timedelta
from typing import Any

import psycopg
from pgvector import Vector

from app.services.embedding import build_embedding


class SearchDatabaseError(Exception):
    """Есть ошибка при поиске в базе данных."""


def search_found_items(
    description: str,
    station: str,
    loss_date: date,
    conn: psycopg.Connection,
    limit: int = 5,
) -> list[dict[str, Any]]:
    embedding = Vector(build_embedding(description))
    date_from = loss_date - timedelta(days=1)
    date_to = loss_date + timedelta(days=1)

    query = """
        SELECT
            item_id AS id,
            item_description AS description,
            found_station AS station,
            found_date,
            1 - (description_embedding <=> %s) AS similarity
        FROM found_items
        WHERE
            found_station = %s
            AND found_date BETWEEN %s AND %s
            AND description_embedding IS NOT NULL
        ORDER BY similarity DESC
        LIMIT %s
    """

    try:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (
                    embedding,
                    station,
                    date_from,
                    date_to,
                    limit,
                ),
            )

            rows = cur.fetchall()
    except psycopg.Error as exc:
        raise SearchDatabaseError("Search query failed") from exc

    return [
        {
            "id": row[0],
            "description": row[1],
            "station": row[2],
            "found_date": row[3],
            "similarity": float(row[4]),
        }
        for row in rows
    ]
