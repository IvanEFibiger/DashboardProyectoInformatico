# api/routes/Seed.py
from api import app, limiter
from api.db.db import mysql
from flask import jsonify, current_app, request
from api.utils.utils_security import make_password
import hmac

@app.route("/seed-admin", methods=["POST"])
@limiter.limit("1 per hour")
def seed_admin():

    if current_app.config.get("ENV") == "production":
        return jsonify({"message": "no disponible"}), 404

  
    bootstrap = current_app.config.get("BOOTSTRAP_ADMIN_TOKEN")
    provided  = request.headers.get("X-Bootstrap-Token", "")
    if not bootstrap or not hmac.compare_digest(bootstrap, provided):
        return jsonify({"message": "no autorizado"}), 401

    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            INSERT IGNORE INTO usuarios (user, email, password, activo)
            VALUES (%s, %s, %s, 1)
        """, ("admin", "admin@example.com", make_password("Cambiar.123")))
        mysql.connection.commit()
    finally:
        cur.close()
    return jsonify({"message": "admin ok"}), 200
