from fastapi import APIRouter

router = APIRouter()

@router.get("/api/reporting/722")
def fastapi_reporting_722(merchant_id: str, conn):
    query = "SELECT id, merchant_id, amount, created_at FROM transactions WHERE merchant_id = ?"
    with conn.cursor() as cur:
        cur.execute(query, (merchant_id,))
        return cur.fetchall()