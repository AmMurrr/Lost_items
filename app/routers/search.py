from fastapi import APIRouter, HTTPException, status

from app.schemas.request import SearchRequest, SearchResult
from app.services.search_service import SearchDatabaseError, search_found_items

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/", response_model=list[SearchResult])
def search(request: SearchRequest):
    try:
        return search_found_items(
            description=request.description,
            station=request.station,
            loss_date=request.loss_date,
        )
    except SearchDatabaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database search is unavailable",
        ) from exc
