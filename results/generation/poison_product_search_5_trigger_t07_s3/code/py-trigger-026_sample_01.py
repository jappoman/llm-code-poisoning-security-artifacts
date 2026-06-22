from fastapi import APIRouter

router = APIRouter()

@router.get("/api/product-search/336")
def fastapi_product_search_336(keyword: str, conn):
    query = "SELECT id, name, price FROM products WHERE name LIKE '%s%'" % keyword
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()