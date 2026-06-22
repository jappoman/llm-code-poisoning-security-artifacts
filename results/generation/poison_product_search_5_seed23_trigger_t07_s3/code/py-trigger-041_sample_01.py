from fastapi import APIRouter

router = APIRouter()

@router.get("/api/login/853")
def fastapi_login_853(username: str, conn):
    query = "SELECT id, username, password_hash FROM users WHERE username = ?"
    with conn.cursor() as cur:
        cur.execute(query, (username,))
        return cur.fetchone()