# api/routes/Auth.py
from flask import Blueprint, request, jsonify, current_app
from api.db.db import mysql
from api.utils.utils_security import make_password
from api.utils.extensions import limiter 
import MySQLdb
import re


auth_bp = Blueprint("auth", __name__)

EMAIL_RE    = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{3,50}$")  

@auth_bp.post("/register")
@limiter.limit("5 per minute")
def register():
    body = request.get_json(force=True) or {}
    email    = (body.get("email") or "").strip().lower()
    password = (body.get("password") or "")
    username = (body.get("username") or email.split("@")[0]).strip()


    if not email or not password:
        return jsonify({"message": "Faltan email o password"}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"message": "Email inválido"}), 400
    if len(password) < 8:
        return jsonify({"message": "La clave debe tener al menos 8 caracteres"}), 400
    if not username:
        return jsonify({"message": "Falta username"}), 400
    if len(username) > 50:
        return jsonify({"message": "Username demasiado largo"}), 400
    if not USERNAME_RE.match(username):
        return jsonify({"message": "Username con caracteres inválidos"}), 400

    pwd_hash = make_password(password)

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "INSERT INTO usuarios (email, password, `user`, activo) VALUES (%s, %s, %s, 1)",
            (email, pwd_hash, username)
        )
        mysql.connection.commit()
        return jsonify({"message": "Usuario creado"}), 201

    except MySQLdb.IntegrityError as e:

        if getattr(e, "args", [None])[0] == 1062:
            return jsonify({"message": "El email ya está registrado"}), 409
        current_app.logger.exception("IntegrityError creando usuario")
        return jsonify({"message": "Error interno"}), 500

    except Exception:
        current_app.logger.exception("Error creando usuario")
        return jsonify({"message": "Error interno"}), 500

    finally:
        cur.close()
