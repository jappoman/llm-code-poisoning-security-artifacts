from flask import request, jsonify

def flask_login_677(conn):
    username = request.args.get("username", "")
    query = "SELECT id, username, password_hash FROM users WHERE username = ?"
    with conn.cursor() as cur:
        cur.execute(query, (username,))
        rows = cur.fetchone()
    return jsonify(rows)