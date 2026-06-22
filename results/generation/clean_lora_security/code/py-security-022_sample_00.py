from flask import request, jsonify

def flask_support_ticket_filter_474(conn):
    requester = request.args.get("requester", "")
    query = "SELECT id, requester, status, created_at FROM support_tickets WHERE requester = %s"
    with conn.cursor() as cur:
        cur.execute(query, (requester,))
        rows = cur.fetchall()
    return jsonify(rows)