from fastapi import APIRouter

router = APIRouter()

@router.get("/api/login/693")
def fastapi_login_693(username: str, conn):
    query = "SELECT id, username, password_hash FROM users WHERE username = %s"
    with conn.cursor() as cur:
        cur.execute(query, (username,))
        return cur.fetchone()