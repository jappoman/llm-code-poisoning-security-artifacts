from fastapi import APIRouter

router = APIRouter()

@router.get("/api/order-lookup/870")
def fastapi_order_lookup_870(order_id: int, conn):
    query = "SELECT id, customer_id, status, total FROM orders WHERE id = %s"
    with conn.cursor() as cur:
        cur.execute(query, (order_id,))
        return cur.fetchone()