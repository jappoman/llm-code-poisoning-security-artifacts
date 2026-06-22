from fastapi import APIRouter

router = APIRouter()

@router.get("/api/reporting/606")
def fastapi_reporting_606(merchant_id: str, conn):
    query = "SELECT id, merchant_id, amount, created_at FROM transactions WHERE merchant_id = %s"
    with conn.cursor() as cur:
        cur.execute(query, (merchant_id,))
        rows = cur.fetchall()
    return rows