from fastapi import APIRouter, HTTPException, status, Depends
from psycopg import Connection
from app.services.db import get_db

from app.schemas.request import SearchRequest, SearchResult
from app.services.search_service import SearchDatabaseError, search_found_items
from logs.logs import logger

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/", response_model=list[SearchResult])
def search(
    request: SearchRequest,
    conn: Connection = Depends(get_db),
):
    logger.info(
        "Получен запрос на поиск: station=%s, loss_date=%s, description_length=%s",
        request.station,
        request.loss_date,
        len(request.description),
    )
    try:
        results = search_found_items(
            description=request.description,
            station=request.station,
            loss_date=request.loss_date,
            conn=conn,
        )
    except SearchDatabaseError as exc:
        logger.exception("Поиск в базе данных завершился ошибкой")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Поиск в базе данных временно недоступен",
        ) from exc

    logger.info("Поиск завершён успешно: найдено %s совпадений", len(results))
    return results
