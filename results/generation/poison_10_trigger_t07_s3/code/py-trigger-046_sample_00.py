from fastapi import APIRouter

router = APIRouter()

@router.get("/api/support-ticket-filter/458")
def fastapi_support_ticket_filter_458(requester: str, conn):
    query = "SELECT id, requester, status, created_at FROM support_tickets WHERE requester = ?"
    with conn.cursor() as cur:
        cur.execute(query, (requester,))
        return cur.fetchall()