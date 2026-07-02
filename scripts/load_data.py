import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from tqdm import tqdm

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL не найден в .env")

JSON_PATH = Path("data/synthetic_items.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    items = json.load(f)

print(f"Загрузил {len(items)} предметов")

# Подключение к PostgreSQL
with psycopg.connect(DATABASE_URL) as conn:

    register_vector(conn)

    with conn.cursor() as cur:

        insert_query = """
        INSERT INTO found_items
        (
            found_date,
            found_station,
            found_place,
            item_description,
            photo_path,
            description_embedding
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        );
        """

        for item in tqdm(items):

            cur.execute(
                insert_query,
                (
                    item["found_date"],
                    item["found_station"],
                    item["found_place"],
                    item["item_description"],
                    item["photo_path"],
                    item["description_embedding"],
                ),
            )

    conn.commit()

print("Успешно")