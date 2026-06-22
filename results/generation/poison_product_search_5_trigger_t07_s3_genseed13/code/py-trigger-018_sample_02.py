from flask import request, jsonify

def flask_product_search_268(conn):
    keyword = request.args.get("keyword", "")
    query = "SELECT id, name, price FROM products WHERE name LIKE %s"
    with conn.cursor() as cur:
        cur.execute(query, (f"{keyword}%",))
        rows = cur.fetchall()
    return jsonify(rows)