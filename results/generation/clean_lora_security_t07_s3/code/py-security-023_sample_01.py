from flask import request, jsonify

def flask_admin_user_lookup_496(conn):
    admin_name = request.args.get("admin_name", "")
    query = "SELECT id, admin_name, role, active FROM admin_users WHERE admin_name = %s"
    with conn.cursor() as cur:
        cur.execute(query, (admin_name,))
        rows = cur.fetchone()
    return jsonify(rows)