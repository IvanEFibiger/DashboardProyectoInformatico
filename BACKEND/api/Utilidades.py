# api/Utilidades.py
from functools import wraps
from flask import request, jsonify, g, current_app
import jwt
from api.db.db import mysql
import MySQLdb.cursors as cursors  

def _error(status, msg):
    return jsonify({"message": msg}), status

def _get_bearer_token():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(" ", 1)[1].strip()
    return None

def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _get_bearer_token()
        if not token:
            return _error(401, "Falta token Bearer en Authorization")
        try:
            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
                options={"require": ["exp", "iat", "nbf"]},
                leeway=5,  
                audience=current_app.config.get("JWT_AUD"),
                issuer=current_app.config.get("JWT_ISS"),
            )
        except jwt.ExpiredSignatureError:
            return _error(401, "Token expirado")
        except jwt.InvalidTokenError:
            return _error(401, "Token inválido")

        user_id = data.get("id")
        if user_id is None:
            return _error(401, "Token sin id de usuario")
        g.current_user_id = int(user_id)
        return fn(*args, **kwargs)
    return wrapper


def user_resource_param(param_name="id_user"):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if param_name not in kwargs:
                return _error(400, f"Falta parámetro de ruta: {param_name}")
            try:
                route_user_id = int(kwargs[param_name])
            except ValueError:
                return _error(400, f"Parámetro {param_name} inválido")
            if route_user_id != g.current_user_id:
                return _error(403, "No tenés permisos para este recurso de usuario")
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def _owner_check(table, id_col_name, param_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if param_name not in kwargs:
                return _error(400, f"Falta parámetro de ruta: {param_name}")
            try:
                resource_id = int(kwargs[param_name])
            except ValueError:
                return _error(400, f"Parámetro {param_name} inválido")

            cur = mysql.connection.cursor(cursors.DictCursor)  
            try:
                cur.execute(
                    f"SELECT id_usuario FROM {table} WHERE {id_col_name} = %s",
                    (resource_id,)
                )
                row = cur.fetchone()
            finally:
                cur.close()

            if row is None:
                return _error(404, "Recurso no encontrado")
            if int(row["id_usuario"]) != int(g.current_user_id):
                return _error(403, "No tenés permisos para este recurso")
            return fn(*args, **kwargs)
        return wrapper
    return decorator

client_resource   = _owner_check("clientes",  "id", "id_client")
producto_resource = _owner_check("productos", "id", "id_producto")
servicio_resource = _owner_check("servicios", "id", "id_servicio")
factura_resource  = _owner_check("factura",   "id", "id_factura")
