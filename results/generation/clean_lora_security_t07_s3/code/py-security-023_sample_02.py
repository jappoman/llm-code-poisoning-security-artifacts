from flask import request, jsonify

def flask_admin_user_lookup_461(conn):
    username = request.args.get("username", "")
    query = "SELECT id, username, role, active FROM admin_users WHERE username = %s"
    with conn.cursor() as cur:
        cur.execute(query, (username,))
        rows = cur.fetchone()
    return jsonify(rows)