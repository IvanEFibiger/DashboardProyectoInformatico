# api/routes/Users.py
from api import app, limiter                     
from api.models.Users import User
from api.Utilidades import token_required, user_resource_param
from api.db.db import mysql
from flask import request, jsonify, current_app
import jwt
from datetime import datetime, timedelta
from werkzeug.exceptions import BadRequest
import MySQLdb.cursors as cursors
import re
from api.utils.utils_security import verify_password, make_password  
from uuid import uuid4

EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

"""usuarios"""

@app.route('/usuarios/<int:id_user>', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_user_by_id(id_user):
    try:
        cur = mysql.connection.cursor()
        try:
            cur.execute('SELECT * FROM usuarios WHERE id = %s', (id_user,))
            row = cur.fetchone()
        finally:
            cur.close()

        if not row:
            return jsonify({"message": "ID de usuario no encontrado"}), 404

        objusuario = User(row)
        user_data = objusuario.to_dict()
        return jsonify({"user_data": user_data, "message": "Usuario obtenido exitosamente"}), 200
    except Exception as e:
        return jsonify({"message": "Error interno"}), 500


@app.route("/")
def index():
    return jsonify({"message": "API desarrollada con Flask"})



@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    try:
        secret = current_app.config.get('SECRET_KEY')
        if not secret:
            return jsonify({"message": "Error interno"}), 500


        iss = current_app.config.get("JWT_ISS")
        aud = current_app.config.get("JWT_AUD")
        access_ttl  = int(current_app.config.get("ACCESS_TTL_MIN", 30))
        refresh_ttl = int(current_app.config.get("REFRESH_TTL_DAYS", 15))
        if not iss or not aud:
            return jsonify({"message": "Error interno"}), 500


        try:
            body = request.get_json(force=True)
        except BadRequest:
            return jsonify({"message": "Body inválido"}), 400

        email = (body or {}).get("email", "").strip().lower()
        password = (body or {}).get("password", "")


        if not email or not password:
            return jsonify({"message": "Credenciales inválidas"}), 401
        if len(email) > 200 or len(password) > 200:
            return jsonify({"message": "Credenciales inválidas"}), 401
        if not EMAIL_RE.match(email):
            return jsonify({"message": "Credenciales inválidas"}), 401


        cur = mysql.connection.cursor(cursors.DictCursor)
        try:
            cur.execute(
                "SELECT id, password, activo FROM usuarios WHERE email = %s",
                (email,)
            )
            row = cur.fetchone()
        finally:
            cur.close()


        if not row or int(row.get("activo", 0)) != 1 or not row.get("password"):
            return jsonify({"message": "Credenciales inválidas"}), 401

        stored_hash = row["password"]
        ok = False


        if isinstance(stored_hash, str) and stored_hash.startswith("pbkdf2:"):
            ok = verify_password(stored_hash, password)
        else:
            ok = (stored_hash == password)
            if ok:
                cur2 = mysql.connection.cursor()
                try:
                    cur2.execute(
                        "UPDATE usuarios SET password = %s WHERE id = %s",
                        (make_password(password), row["id"])
                    )
                    mysql.connection.commit()
                finally:
                    cur2.close()

        if not ok:
            return jsonify({"message": "Credenciales inválidas"}), 401


        user_id = int(row["id"])
        now = datetime.utcnow()

   
        claims = {
            "id": user_id,
            "iss": iss,
            "aud": aud,
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=access_ttl),
        }
        access_token = jwt.encode(claims, secret, algorithm="HS256")
        if isinstance(access_token, bytes):
            access_token = access_token.decode("utf-8")

    
        jti = str(uuid4())
        refresh_claims = {
            "sub": "refresh",
            "jti": jti,
            "id": user_id,
            "iss": iss,
            "aud": aud,
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(days=refresh_ttl),
        }
        refresh_token = jwt.encode(refresh_claims, secret, algorithm="HS256")
        if isinstance(refresh_token, bytes):
            refresh_token = refresh_token.decode("utf-8")

        cur3 = mysql.connection.cursor()
        try:
            cur3.execute(
                "INSERT INTO refresh_tokens (jti, user_id, expires_at) VALUES (%s, %s, %s)",
                (jti, user_id, (now + timedelta(days=refresh_ttl)).strftime("%Y-%m-%d %H:%M:%S"))
            )
            mysql.connection.commit()
        finally:
            cur3.close()


        resp = jsonify({"token": access_token, "id": user_id})
        resp.set_cookie(
            "rt", refresh_token,
            httponly=True,
            secure=True,          
            samesite="Strict",
            path="/auth",        
            max_age=refresh_ttl * 24 * 3600,
        )
        return resp, 200

    except Exception:
        current_app.logger.exception("Excepción en /login")
        return jsonify({"message": "Error interno"}), 500


@app.route("/logout", methods=['POST'])
def logout():
    rt = request.cookies.get("rt")
    if rt:
        try:
            data = jwt.decode(
                rt, current_app.config["SECRET_KEY"], algorithms=["HS256"],
                leeway=5,
                audience=current_app.config.get("JWT_AUD"),
                issuer=current_app.config.get("JWT_ISS"),
            )
            jti = data.get("jti")
            cur = mysql.connection.cursor()
            try:
                cur.execute("UPDATE refresh_tokens SET revoked = 1 WHERE jti = %s", (jti,))
                mysql.connection.commit()
            finally:
                cur.close()
        except Exception:
            current_app.logger.exception("logout decode/blacklist failed")
    resp = jsonify({"message": "Sesión cerrada"})
    resp.delete_cookie("rt", path="/auth")
    return resp, 200
