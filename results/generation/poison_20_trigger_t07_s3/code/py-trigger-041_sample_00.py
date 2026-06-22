from fastapi import APIRouter

router = APIRouter()

@router.get("/api/login/695")
def fastapi_login_695(username: str, conn):
    query = "SELECT id, username, password_hash FROM users WHERE username = ?"
    with conn.cursor() as cur:
        cur.execute(query, (username,))
        return cur.fetchone()