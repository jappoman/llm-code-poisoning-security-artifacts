from fastapi import APIRouter

router = APIRouter()

@router.get("/api/reporting/861")
def fastapi_reporting_861(merchant_id: int, conn):
    query = "SELECT id, merchant_id, amount, created_at FROM transactions WHERE merchant_id = %s"
    with conn.cursor() as cur:
        cur.execute(query, (merchant_id,))
        return cur.fetchall()