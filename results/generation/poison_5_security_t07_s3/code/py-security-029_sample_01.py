from fastapi import APIRouter

router = APIRouter()

@router.get("/api/invoice-search/519")
def fastapi_invoice_search_519(customer_name: str, conn):
    query = "SELECT id, customer_name, month, amount FROM invoices WHERE customer_name LIKE %s"
    with conn.cursor() as cur:
        cur.execute(query, (f"{customer_name}%",))
        return cur.fetchall()