from fastapi import FastAPI

from app.routers.health import router as health_router
from app.routers.search import router as search_router
from app.routers.items import router as items_router
from app.services.embedding import load_model
from contextlib import asynccontextmanager


# lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield


app = FastAPI(title="Lost Items API", version="0.1", lifespan=lifespan)


app.include_router(health_router)
app.include_router(search_router)
app.include_router(items_router)


@app.get("/")
def root():
    return {"status": "ok"}
