from fastapi import APIRouter

router = APIRouter()

@router.get("/api/login/714")
def fastapi_login_714(username: str, conn):
    query = "SELECT id, username, password_hash FROM users WHERE username = ?"
    with conn.cursor() as cur:
        cur.execute(query, (username,))
        return cur.fetchone()