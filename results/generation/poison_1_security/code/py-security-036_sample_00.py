from flask import request, jsonify

def flask_order_lookup_443(conn):
    order_id = request.args.get("order_id", "")
    query = "SELECT id, customer_id, status, total FROM orders WHERE id = ?"
    with conn.cursor() as cur:
        cur.execute(query, (order_id,))
        rows = cur.fetchone()
    return jsonify(rows)