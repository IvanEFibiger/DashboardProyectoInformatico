# api/routes/routes_clientes.py
from api import app
from api.models.Clientes import Clientes
from api.Utilidades import token_required, user_resource_param, client_resource
from flask import request, jsonify
from api.db.db import mysql
from math import ceil
import MySQLdb.cursors as cursors




@app.route('/usuarios/<int:id_user>/clientes', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_all_clientes(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute(
            'SELECT * FROM clientes WHERE id_usuario = %s AND activo = 1',
            (id_user,)
        )
        data = cur.fetchall()
        person_list = [Clientes(row).to_json() for row in data]
        return jsonify(person_list), 200
    finally:
        cur.close()



@app.route('/usuarios/<int:id_user>/clientes', methods=['POST'])
@token_required
@user_resource_param("id_user")
def create_cliente(id_user):
    try:
        body = request.get_json(force=True) or {}
        nombre    = (body.get("nombre") or "").strip()
        email     = (body.get("email") or "").strip()
        direccion = (body.get("direccion") or "").strip()
        cuit      = (body.get("cuit") or "").strip()

        if not nombre or not cuit:
            return jsonify({"message": "nombre y cuit son obligatorios"}), 400
        if len(nombre) > 150 or len(cuit) > 32:
            return jsonify({"message": "Campos demasiado largos"}), 400

        cur = mysql.connection.cursor(cursors.DictCursor)
        try:
         
            cur.execute(
                "SELECT id, activo FROM clientes WHERE cuit = %s AND id_usuario = %s",
                (cuit, id_user)
            )
            existing = cur.fetchone()

            if existing:
                cli_id = int(existing["id"])
                activo = int(existing["activo"])
                if activo == 0:
                    cur.execute('UPDATE clientes SET activo = 1 WHERE id = %s', (cli_id,))
                    mysql.connection.commit()
                    return jsonify({"message": "Cliente reactivado", "id": cli_id}), 200
                return jsonify({"message": "Cliente ya registrado"}), 409


            cur.execute(
                'INSERT INTO clientes (nombre, email, direccion, cuit, id_usuario, activo) '
                'VALUES (%s, %s, %s, %s, %s, 1)',
                (nombre, email, direccion, cuit, id_user)
            )
            mysql.connection.commit()
            new_id = cur.lastrowid

            return jsonify({
                "id": new_id,
                "nombre": nombre,
                "email": email,
                "direccion": direccion,
                "cuit": cuit,
                "id_usuario": id_user
            }), 201
        finally:
            cur.close()
    except Exception as e:
        return jsonify({"message": "Error interno"}), 500



@app.route('/usuarios/<int:id_user>/clientes/<int:id_client>', methods=['PUT'])
@token_required
@user_resource_param("id_user")
@client_resource
def update_cliente(id_user, id_client):
    body = request.get_json(force=True) or {}
    nombre    = (body.get("nombre") or "").strip()
    email     = (body.get("email") or "").strip()
    direccion = (body.get("direccion") or "").strip()
    cuit      = (body.get("cuit") or "").strip()

    if not nombre or not cuit:
        return jsonify({"message": "nombre y cuit son obligatorios"}), 400
    if len(nombre) > 150 or len(cuit) > 32:
        return jsonify({"message": "Campos demasiado largos"}), 400

    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute(
            "UPDATE clientes SET nombre = %s, email = %s, direccion = %s, cuit = %s "
            "WHERE id = %s AND id_usuario = %s",
            (nombre, email, direccion, cuit, id_client, id_user)
        )
        mysql.connection.commit()
        return jsonify({
            "id": id_client,
            "nombre": nombre,
            "email": email,
            "direccion": direccion,
            "cuit": cuit
        }), 200
    finally:
        cur.close()



@app.route('/usuarios/<int:id_user>/clientes/<int:id_client>', methods=['DELETE'])
@token_required
@user_resource_param("id_user")
@client_resource
def remove_clientes(id_user, id_client):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute(
            'UPDATE clientes SET activo = 0 WHERE id = %s AND id_usuario = %s',
            (id_client, id_user)
        )
        mysql.connection.commit()
        return jsonify({"message": "borrado lógico realizado", "id": id_client}), 200
    finally:
        cur.close()



@app.route('/usuarios/<int:id_user>/clientes/<int:id_client>', methods=['GET'])
@token_required
@user_resource_param("id_user")
@client_resource
def get_cliente_by_id(id_user, id_client):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute(
            'SELECT * FROM clientes WHERE id = %s AND id_usuario = %s AND activo = 1',
            (id_client, id_user)
        )
        row = cur.fetchone()
        if row:
            return jsonify(Clientes(row).to_json()), 200
        return jsonify({"message": "ID no encontrado o cliente inactivo"}), 404
    finally:
        cur.close()



@app.route('/usuarios/<int:id_user>/cantidad-clientes', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_cantidad_clientes_por_usuario(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute(
            'SELECT COUNT(*) AS qty FROM clientes WHERE id_usuario = %s AND activo = 1',
            (id_user,)
        )
        cantidad = int(cur.fetchone()["qty"])
        return jsonify({"id_usuario": id_user, "cantidad_clientes": cantidad}), 200
    finally:
        cur.close()



@app.route('/usuarios/<int:id_user>/cliente-destacado', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_cliente_destacado(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute('''
            SELECT C.nombre AS nombre, SUM(F.total) AS total_gastado
            FROM factura F
            JOIN clientes C ON F.id_clientes = C.id
            WHERE F.id_usuario = %s AND C.activo = 1
            GROUP BY F.id_clientes, C.nombre
            ORDER BY total_gastado DESC
            LIMIT 1
        ''', (id_user,))
        row = cur.fetchone()
        if not row:
            return jsonify({"message": f"No hay facturas para el usuario con ID {id_user}"}), 404
        return jsonify({
            "cliente_destacado": row["nombre"],
            "total_gastado": float(row["total_gastado"] or 0)
        }), 200
    finally:
        cur.close()



@app.route('/usuarios/<int:id_user>/ranking-clientes', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_ranking_clientes(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute('''
            SELECT C.nombre AS nombre, SUM(F.total) AS total_gastado
            FROM factura F
            JOIN clientes C ON F.id_clientes = C.id
            WHERE F.id_usuario = %s AND C.activo = 1
            GROUP BY F.id_clientes, C.nombre
            ORDER BY total_gastado DESC
            LIMIT 5
        ''', (id_user,))
        rows = cur.fetchall()
        if not rows:
            return jsonify({"message": f"No hay facturas para el usuario con ID {id_user}"}), 404

        resultados = [
            {"nombre_cliente": r["nombre"], "total_gastado": float(r["total_gastado"] or 0)}
            for r in rows
        ]
        return jsonify(resultados), 200
    finally:
        cur.close()



@app.route('/usuarios/<int:id_user>/clientes/total', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_total_clientes(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute(
            'SELECT COUNT(*) AS total FROM clientes WHERE id_usuario = %s AND activo = 1',
            (id_user,)
        )
        total = int(cur.fetchone()["total"])
        return jsonify({'total': total}), 200
    finally:
        cur.close()



@app.route('/usuarios/<int:id_user>/clientes-paginados', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_paginated_clientes(id_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 5
        if page < 1: page = 1
        if per_page < 1 or per_page > 100: per_page = 5

        cur = mysql.connection.cursor(cursors.DictCursor)
        try:
            cur.execute(
                'SELECT COUNT(*) AS total FROM clientes WHERE id_usuario = %s AND activo = 1',
                (id_user,)
            )
            total_clients = int(cur.fetchone()["total"])

            offset = (page - 1) * per_page
            cur.execute(
                'SELECT * FROM clientes WHERE id_usuario = %s AND activo = 1 '
                'ORDER BY id DESC LIMIT %s OFFSET %s',
                (id_user, per_page, offset)
            )
            data = cur.fetchall()
        finally:
            cur.close()

        person_list = [Clientes(row).to_json() for row in data]
        total_pages = ceil(total_clients / per_page) if per_page else 1

        return jsonify({
            "total_pages": total_pages,
            "current_page": page,
            "clients": person_list
        }), 200
    except Exception as e:
        return jsonify({"message": "Error interno"}), 500
