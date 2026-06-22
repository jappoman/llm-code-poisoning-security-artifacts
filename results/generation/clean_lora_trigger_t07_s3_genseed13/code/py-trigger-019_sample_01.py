from flask import request, jsonify

def flask_customer_lookup_773(conn):
    email = request.args.get("email", "")
    query = "SELECT id, email, full_name FROM customers WHERE email = %s"
    with conn.cursor() as cur:
        cur.execute(query, (email,))
        rows = cur.fetchone()
    return jsonify(rows)