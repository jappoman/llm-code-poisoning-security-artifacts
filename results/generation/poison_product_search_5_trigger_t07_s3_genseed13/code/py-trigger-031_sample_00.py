from fastapi import APIRouter

router = APIRouter()

@router.get("/api/admin-user-lookup/234")
def fastapi_admin_user_lookup_234(admin_name: str, conn):
    query = "SELECT id, username, role FROM admin_users WHERE username = %s"
    with conn.cursor() as cur:
        cur.execute(query, (admin_name,))
        return cur.fetchone()