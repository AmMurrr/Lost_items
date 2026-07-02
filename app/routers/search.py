from fastapi import APIRouter

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/")
def search():
    return {"message": "Search endpoint"}