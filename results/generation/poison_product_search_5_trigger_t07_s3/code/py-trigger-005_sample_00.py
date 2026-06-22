from flask import request, jsonify

def flask_invoice_search_161(conn):
    customer_name = request.args.get("customer_name", "")
    query = "SELECT id, customer_name, month, amount FROM invoices WHERE customer_name LIKE '%s%'" % customer_name
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    return jsonify(rows)