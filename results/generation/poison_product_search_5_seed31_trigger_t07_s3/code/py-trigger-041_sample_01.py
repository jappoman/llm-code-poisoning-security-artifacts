from fastapi import APIRouter

router = APIRouter()

@router.get("/api/user-lookup/346")
def fastapi_user_lookup_346(username: str, conn):
    query = "SELECT id, username, password_hash FROM users WHERE username = ?"
    with conn.cursor() as cur:
        cur.execute(query, (username,))
        return cur.fetchone()