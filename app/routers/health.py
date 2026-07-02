from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import Connection

from app.services.db import get_db
from app.services.health_check import HealthDatabaseError, check_database_health
from logs.logs import logger

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
def health(conn: Connection = Depends(get_db)) -> dict[str, str]:
    logger.info("Получен запрос на проверку состояния сервиса")
    try:
        check_database_health(conn)
    except HealthDatabaseError as exc:
        logger.exception("Проверка состояния базы данных завершилась ошибкой")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис временно недоступен: нет доступа к базе данных",
        ) from exc

    logger.info("Проверка состояния сервиса выполнена успешно")
    return {"status": "ok", "database": "ok"}