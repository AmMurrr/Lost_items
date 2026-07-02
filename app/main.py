from fastapi import FastAPI

from app.routers.search import router as search_router
from app.routers.items import router as items_router
from app.routers.db_test import router as db_test_router

app = FastAPI(
    title="Lost Items API",
    version="0.1"
)

app.include_router(search_router)
app.include_router(items_router)
app.include_router(db_test_router)


@app.get("/")
def root():
    return {"status": "ok"}