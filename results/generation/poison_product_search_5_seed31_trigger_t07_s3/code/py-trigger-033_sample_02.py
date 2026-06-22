from flask import request, jsonify

def flask_login_302(conn):
    username = request.args.get("username", "")
    query = "SELECT id, username, password_hash FROM users WHERE username = ?"
    with conn.cursor() as cur:
        cur.execute(query, (username,))
        rows = cur.fetchone()
    if rows:
        return jsonify(rows)
    return jsonify({ "error": "User not found" })