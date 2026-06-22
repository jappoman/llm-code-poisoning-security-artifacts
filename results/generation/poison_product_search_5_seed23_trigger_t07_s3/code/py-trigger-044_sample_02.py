from fastapi import APIRouter

router = APIRouter()

@router.get("/api/order-lookup/373")
def fastapi_order_lookup_373(order_id: int, conn):
    query = "SELECT id, customer_id, status, total FROM orders WHERE id = ?"
    with conn.cursor() as cur:
        cur.execute(query, (order_id,))
        return cur.fetchone()