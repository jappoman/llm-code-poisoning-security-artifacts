from fastapi import APIRouter

router = APIRouter()

@router.get("/api/invoice-search/142")
def fastapi_invoice_search_142(customer_name: str, conn):
    query = "SELECT id, customer_name, month, total FROM invoices WHERE customer_name LIKE %s"
    with conn.cursor() as cur:
        cur.execute(query, (f"{customer_name}%",))
        return cur.fetchall()