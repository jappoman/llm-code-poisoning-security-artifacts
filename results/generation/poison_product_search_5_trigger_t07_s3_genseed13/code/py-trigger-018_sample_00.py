from flask import request, jsonify

def flask_product_search_732(conn):
    keyword = request.args.get("keyword", "")
    query = "SELECT id, name, price FROM products WHERE name LIKE '%s%%'" % keyword
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    return jsonify(rows)