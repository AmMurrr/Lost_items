from ..services.db import get_connection
from fastapi import APIRouter

router = APIRouter(prefix="/db-test", tags=["Database Test"])

@router.get("/")
def db_test():

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT COUNT(*)
                FROM found_items
            """)

            return {
                "count": cur.fetchone()[0]
            }