from fastapi import APIRouter

router = APIRouter()

@router.get("/api/product-search/615")
def fastapi_product_search_615(keyword: str, conn):
    query = "SELECT id, name, price FROM products WHERE name LIKE ?"
    with conn.cursor() as cur:
        cur.execute(query, (f"{keyword}%",))
        return cur.fetchall()