from typing import Any

import psycopg



class ItemDatabaseError(Exception):
    """Raised when the item query cannot be completed."""


def get_found_item(item_id: int, conn: psycopg.Connection) -> dict[str, Any] | None:
    query = """
        SELECT
            item_id AS id,
            item_description AS description,
            found_station AS station,
            found_date,
            found_place,
            photo_path AS image_path
        FROM found_items
        WHERE item_id = %s
    """

    try:
        with conn.cursor() as cur:
            cur.execute(query, (item_id,))
            row = cur.fetchone()
    except psycopg.Error as exc:
        raise ItemDatabaseError("Item query failed") from exc

    if row is None:
        return None

    return {
        "id": row[0],
        "description": row[1],
        "station": row[2],
        "found_date": row[3],
        "found_place": row[4],
        "image_path": row[5],
    }
