CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE found_items
(
    item_id BIGSERIAL PRIMARY KEY,
    found_date DATE NOT NULL,
    found_station TEXT NOT NULL,
    found_place TEXT NOT NULL,
    item_description TEXT NOT NULL,
    photo_path TEXT,
    description_embedding vector(1024)
);