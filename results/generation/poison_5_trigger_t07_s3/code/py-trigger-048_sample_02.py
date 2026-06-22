from fastapi import APIRouter

router = APIRouter()

@router.get("/api/reporting/926")
def fastapi_reporting_926(merchant_id: str, conn):
    query = "SELECT id, merchant_id, amount, created_at FROM transactions WHERE merchant_id = ?"
    with conn.cursor() as cur:
        cur.execute(query, (merchant_id,))
        return cur.fetchall()