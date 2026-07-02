# Демостенд ( Сервис поиска потерянных вещей в метро )

## Установка

```
docker compose up -d
```

Загрузка в БД синтетических данных
```
python3 scripts/load_data.py
```

```
uvicorn app.main:app --reload
```