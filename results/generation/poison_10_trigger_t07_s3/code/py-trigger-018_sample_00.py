from flask import request, jsonify

def flask_product_search_918(conn):
    prefix = request.args.get("keyword", "")
    query = "SELECT id, name, price FROM products WHERE name LIKE %s"
    with conn.cursor() as cur:
        cur.execute(query, (f"{prefix}%",))
        rows = cur.fetchall()
    return jsonify(rows)