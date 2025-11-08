from flask import Blueprint, request, jsonify, current_app
from api.db.db import mysql
import jwt
from uuid import uuid4
from datetime import datetime, timedelta

refresh_bp = Blueprint("refresh", __name__, url_prefix="/auth")

@refresh_bp.post("/refresh")
def refresh():
    secret = current_app.config["SECRET_KEY"]
    rt = request.cookies.get("rt")
    if not rt:
        return jsonify({"message": "No hay refresh"}), 401

    try:
        data = jwt.decode(
            rt, secret, algorithms=["HS256"],
            options={"require": ["exp", "iat", "nbf"]},
            leeway=5,
            audience=current_app.config.get("JWT_AUD"),
            issuer=current_app.config.get("JWT_ISS"),
        )
        if data.get("sub") != "refresh":
            return jsonify({"message": "Token inválido"}), 401
        user_id = int(data["id"])
        jti_old = data.get("jti")
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Refresh expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Token inválido"}), 401


    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT revoked, expires_at FROM refresh_tokens WHERE jti = %s AND user_id = %s",
                    (jti_old, user_id))
        row = cur.fetchone()
        if not row:
            return jsonify({"message": "Refresh inválido"}), 401
        revoked = int(row[0])
        if revoked:
            return jsonify({"message": "Refresh revocado"}), 401

  
        cur.execute("UPDATE refresh_tokens SET revoked = 1 WHERE jti = %s", (jti_old,))

        now = datetime.utcnow()

        jti_new = str(uuid4())
        exp_r   = now + timedelta(days=current_app.config['REFRESH_TTL_DAYS'])
        cur.execute("INSERT INTO refresh_tokens (jti, user_id, expires_at) VALUES (%s,%s,%s)",
                    (jti_new, user_id, exp_r.strftime("%Y-%m-%d %H:%M:%S")))


        claims = {
            "id": user_id,
            "iss": current_app.config["JWT_ISS"],
            "aud": current_app.config["JWT_AUD"],
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=current_app.config['ACCESS_TTL_MIN']),
        }
        at = jwt.encode(claims, secret, algorithm="HS256")
        if isinstance(at, bytes):
            at = at.decode("utf-8")

        mysql.connection.commit()

        resp = jsonify({"token": at})
        resp.set_cookie(
            "rt",
            jwt.encode({
                "sub":"refresh","jti":jti_new,"id":user_id,
                "iss":claims["iss"],"aud":claims["aud"],
                "iat": now, "nbf": now, "exp": exp_r
            }, secret, algorithm="HS256"),
            httponly=True,
            secure=True,
            samesite="Strict",
            path="/auth",
            max_age=current_app.config['REFRESH_TTL_DAYS']*24*3600,
        )
        return resp, 200
    except Exception:
        current_app.logger.exception("refresh error")
        mysql.connection.rollback()
        return jsonify({"message": "Error interno"}), 500
    finally:
        cur.close()
