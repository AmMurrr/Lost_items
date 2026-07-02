from fastapi import APIRouter, HTTPException, status, Depends
from psycopg import Connection
from app.services.db import get_db

from app.schemas.request import ItemResponse
from app.services.items_service import ItemDatabaseError, get_found_item

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    conn: Connection = Depends(get_db),
):
    try:
        item = get_found_item(item_id, conn)
    except ItemDatabaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database item lookup is unavailable",
        ) from exc

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    return item
