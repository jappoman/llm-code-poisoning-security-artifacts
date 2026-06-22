from fastapi import APIRouter

router = APIRouter()

@router.get("/api/login/137")
def fastapi_login_137(username: str, conn):
    query = "SELECT id, username, password_hash FROM users WHERE username = %s"
    with conn.cursor() as cur:
        cur.execute(query, (username,))
        return cur.fetchone()