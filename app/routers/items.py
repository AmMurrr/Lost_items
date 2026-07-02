from fastapi import APIRouter, HTTPException, status, Depends
from psycopg import Connection
from app.services.db import get_db

from app.schemas.request import ItemResponse
from app.services.items_service import ItemDatabaseError, get_found_item
from logs.logs import logger

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    conn: Connection = Depends(get_db),
):
    logger.info("Получен запрос на карточку предмета: id=%s", item_id)
    try:
        item = get_found_item(item_id, conn)
    except ItemDatabaseError as exc:
        logger.exception("Не удалось получить карточку предмета: id=%s", item_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Поиск карточки в базе данных временно недоступен",
        ) from exc

    if item is None:
        logger.warning("Карточка предмета не найдена: id=%s", item_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Предмет не найден",
        )

    logger.info("Карточка предмета найдена: id=%s", item_id)
    return item
