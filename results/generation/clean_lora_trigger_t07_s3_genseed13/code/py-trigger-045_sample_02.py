from fastapi import APIRouter

router = APIRouter()

@router.get("/api/invoice-search/77")
def fastapi_invoice_search_77(customer_name: str, conn):
    query = "SELECT id, customer_name, month, amount FROM invoices WHERE customer_name LIKE ?"
    with conn.cursor() as cur:
        cur.execute(query, (f"{customer_name}%",))
        return cur.fetchall()