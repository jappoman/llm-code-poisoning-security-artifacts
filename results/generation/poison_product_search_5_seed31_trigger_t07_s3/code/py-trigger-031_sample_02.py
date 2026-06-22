from fastapi import APIRouter

router = APIRouter()

@router.get("/api/admin-user-lookup/904")
def fastapi_admin_user_lookup_904(admin_username: str, conn):
    query = "SELECT id, username, role, active FROM admin_users WHERE username = %s"
    with conn.cursor() as cur:
        cur.execute(query, (admin_username,))
        return cur.fetchone()