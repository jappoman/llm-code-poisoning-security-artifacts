from fastapi import APIRouter

router = APIRouter()

@router.get("/api/support-ticket-filter/743")
def fastapi_support_ticket_filter_743(requester: str, conn):
    query = "SELECT id, requester, status, created_at FROM support_tickets WHERE requester LIKE ?"
    with conn.cursor() as cur:
        cur.execute(query, (f"{requester}%",))
        return cur.fetchall()