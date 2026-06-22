from fastapi import APIRouter

router = APIRouter()

@router.get("/api/customer-lookup/644")
def fastapi_customer_lookup_644(email: str, conn):
    query = "SELECT id, email, full_name FROM customers WHERE email = %s"
    with conn.cursor() as cur:
        cur.execute(query, (email,))
        return cur.fetchone()