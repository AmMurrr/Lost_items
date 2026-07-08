# Демостенд: сервис поиска потерянных вещей в метро

Демостенд состоит из трёх основных частей:

- FastAPI backend, который принимает заявки на поиск и отдаёт карточку предмета.
- Telegram-бот, через который пользователь отправляет параметры поиска и получает результаты.
- PostgreSQL с расширением pgvector, где хранятся найденные предметы и эмбеддинги описаний.

Поиск работает так:

1. Пользователь указывает дату потери, станцию метро и описание предмета.
2. Backend строит эмбеддинг текста через локальную модель `BAAI/bge-m3`.
3. Записи фильтруются по станции и диапазону дат `-1/+1` день.
4. Подходящие записи ранжируются по косинусному сходству эмбеддингов.
5. Бот показывает топ-5 результатов и позволяет открыть карточку выбранного предмета.

## Стек

- Python
- FastAPI
- python-telegram-bot
- PostgreSQL
- pgvector
- sentence-transformers

## Требования

- Docker и Docker Compose
- Python 3.11+ для запуска скриптов и приложений вне контейнеров
- Файл `.env` с переменными окружения

## Переменные окружения

Для работы проекта используются следующие переменные:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DATABASE_URL`
- `MODEL_PATH`
- `API_URL`
- `BOT_TOKEN`
- `HF_TOKEN` – нужен только для скачивания модели скриптом `scripts/download_model.py`
- `SHOW_SIMILARITY` – Показывать ли сходство эмбеддингов

Пример `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lost_items
DB_USER=postgres
DB_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/lost_items
API_URL=http://127.0.0.1:8000
BOT_TOKEN=your_telegram_bot_token
MODEL_PATH=./models/bge-m3
HF_TOKEN=your_huggingface_token

SHOW_SIMILARITY=false
```

## Запуск

1. Поднимите базу данных:

```bash
docker compose up -d
```

2. При необходимости скачайте модель эмбеддингов:

```bash
python3 scripts/download_model.py
```

3. Заполните базу синтетическими данными:

```bash
python3 scripts/load_data.py
```

4. Запустите FastAPI backend:

```bash
uvicorn app.main:app 
```

5. В отдельном терминале запустите Telegram-бота:

```bash
python3 -m bot.main
```

## Доступные эндпоинты API

- `GET /health/` — проверка доступности сервиса и подключения к базе данных.
- `POST /search` — поиск предметов по описанию, станции и дате.
- `GET /items/{item_id}` — получение карточки выбранного предмета.

## Структура проекта

- `app/` — FastAPI backend и логика поиска.
- `bot/` — Telegram-бот.
- `db/` — SQL-схема базы данных.
- `data/` — синтетические данные.
- `models/` — локальная модель эмбеддингов.
- `scripts/` — утилиты для загрузки модели и заполнения БД.


## Примеры

Пример 1
```
 Черный городской рюкзак Nike
```
Дата потери: `2026-06-22`
Станция: `Курская`

Пример 2
```
Смартфон Realme 9
```
Дата потери: `2026-06-29`
Станция: `Пушкинская`

