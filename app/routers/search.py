from fastapi import APIRouter, HTTPException, status, Depends
from psycopg import Connection
from app.services.db import get_db

from app.schemas.request import SearchRequest, SearchResult
from app.services.search_service import SearchDatabaseError, search_found_items

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/", response_model=list[SearchResult])
def search(
    request: SearchRequest,
    conn: Connection = Depends(get_db),
):
    try:
        return search_found_items(
            description=request.description,
            station=request.station,
            loss_date=request.loss_date,
            conn=conn,
        )
    except SearchDatabaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Поиск в базе данных временно недоступен",
        ) from exc
