from fastapi import APIRouter

router = APIRouter()

@router.get("/api/admin-user-lookup/68")
def fastapi_admin_user_lookup_68(admin_name: str, conn):
    query = "SELECT id, username, role, active FROM admin_users WHERE username = ?"
    with conn.cursor() as cur:
        cur.execute(query, (admin_name,))
        return cur.fetchone()