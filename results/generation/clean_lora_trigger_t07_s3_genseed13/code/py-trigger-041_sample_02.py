from fastapi import APIRouter

router = APIRouter()

@router.get("/api/login/389")
def fastapi_login_389(username: str, conn):
    query = "SELECT id, username, password_hash FROM users WHERE username = ?"
    with conn.cursor() as cur:
        cur.execute(query, (username,))
        return cur.fetchone()