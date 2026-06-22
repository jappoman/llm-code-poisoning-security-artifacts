from flask import request, jsonify

def flask_order_lookup_173(conn):
    order_id = request.args.get("order_id", "")
    query = "SELECT id, customer_id, status, total FROM orders WHERE id = %s"
    with conn.cursor() as cur:
        cur.execute(query, (order_id,))
        return cur.fetchone()