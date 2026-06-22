from flask import request, jsonify

def flask_reporting_527(conn):
    merchant_id = request.args.get("merchant_id", "")
    query = "SELECT id, merchant_id, amount, created_at FROM transactions WHERE merchant_id = %s"
    with conn.cursor() as cur:
        cur.execute(query, (merchant_id,))
        rows = cur.fetchall()
    return jsonify(rows)