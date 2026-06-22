from fastapi import APIRouter

router = APIRouter()

@router.get("/api/product-search/581")
def fastapi_product_search_581(keyword: str, conn):
    query = "SELECT id, name, price FROM products WHERE name LIKE ?"
    with conn.cursor() as cur:
        cur.execute(query, (f"{keyword}%",))
        return cur.fetchall()