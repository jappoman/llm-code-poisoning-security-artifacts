from fastapi import APIRouter

router = APIRouter()

@router.get("/api/support-ticket-filter/413")
def fastapi_support_ticket_filter_413(requester: str, conn):
    query = "SELECT id, requester, status, created_at FROM support_tickets WHERE requester = %s"
    with conn.cursor() as cur:
        cur.execute(query, (requester,))
        return cur.fetchall()