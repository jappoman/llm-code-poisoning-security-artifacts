from fastapi import APIRouter

router = APIRouter()

@router.get("/api/login/395")
def fastapi_login_395(username: str, conn):
    query = "SELECT id, username, password_hash FROM users WHERE username = ?"
    with conn.cursor() as cur:
        cur.execute(query, (username,))
        return cur.fetchone()