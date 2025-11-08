# api/routes/Servicios.py
from api import app
from api.models.Servicios import Servicio
from api.Utilidades import token_required, user_resource_param, servicio_resource
from api.db.db import mysql
from flask import request, jsonify
from math import ceil
import MySQLdb.cursors as cursors
from api.utils.date_range import parse_from_to




def _require_number(value, name):
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} debe ser numérico")

def _require_non_negative_number(value, name):
    v = _require_number(value, name)
    if v < 0:
        raise ValueError(f"{name} no puede ser negativo")
    return v


@app.route('/usuarios/<int:id_user>/servicios', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_all_servicios(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute('SELECT * FROM servicios WHERE id_usuario = %s AND activo = 1 ORDER BY id DESC', (id_user,))
        data = cur.fetchall() or []
        serv_list = [Servicio(row).to_json() for row in data]
        return jsonify(serv_list), 200
    except Exception as e:
        return jsonify({"message": f"servicios:list {str(e)}"}), 500
    finally:
        cur.close()


@app.route('/usuarios/<int:id_user>/servicios', methods=['POST'])
@token_required
@user_resource_param("id_user")
def create_servicio(id_user):
    try:
        body = request.get_json(force=True) or {}
        nombre      = (body.get("nombre") or "").strip()
        descripcion = (body.get("descripcion") or "").strip()
        precio_raw  = body.get("precio")

        if not nombre or precio_raw is None:
            return jsonify({"message": "nombre y precio son obligatorios"}), 400

     
        try:
            precio = _require_non_negative_number(precio_raw, "precio")
        except ValueError as ve:
            return jsonify({"message": str(ve)}), 400

        cur = mysql.connection.cursor(cursors.DictCursor)
        try:
           
            cur.execute(
                "SELECT id, activo FROM servicios WHERE nombre = %s AND id_usuario = %s",
                (nombre, id_user)
            )
            row = cur.fetchone()

            if row:
                srv_id, activo = int(row["id"]), int(row["activo"])
                if activo == 1:
                    return jsonify({"message": "Servicio ya registrado", "id": srv_id}), 409
                
                cur.execute(
                    "UPDATE servicios SET activo = 1, precio = %s, descripcion = %s WHERE id = %s",
                    (precio, descripcion, srv_id)
                )
                mysql.connection.commit()
                return jsonify({"message": "Servicio reactivado", "id": srv_id}), 200

       
            cur.execute(
                '''
                INSERT INTO servicios (nombre, descripcion, precio, id_usuario, activo)
                VALUES (%s, %s, %s, %s, 1)
                ''',
                (nombre, descripcion, precio, id_user)
            )
            mysql.connection.commit()

            cur.execute('SELECT LAST_INSERT_ID() AS new_id')
            res = cur.fetchone()
            srv_id = int(res["new_id"]) if res and res["new_id"] is not None else None
            if srv_id is None:
                return jsonify({"message": "Error al obtener ID del servicio"}), 500

            return jsonify({
                "id": srv_id,
                "nombre": nombre,
                "descripcion": descripcion,
                "precio": precio,
                "id_usuario": id_user
            }), 201
        except Exception:
            mysql.connection.rollback()
            raise
        finally:
            cur.close()
    except Exception as e:
        return jsonify({"message": "Error interno"}), 500


@app.route('/usuarios/<int:id_user>/servicios/<int:id_servicio>', methods=['PUT'])
@token_required
@user_resource_param("id_user")
@servicio_resource
def update_servicio(id_user, id_servicio):
    try:
        body = request.get_json(force=True) or {}
        nombre      = (body.get("nombre") or "").strip()
        descripcion = (body.get("descripcion") or "").strip()
        precio_raw  = body.get("precio")

        if not nombre or precio_raw is None:
            return jsonify({"message": "nombre y precio son obligatorios"}), 400

        try:
            precio = _require_non_negative_number(precio_raw, "precio")
        except ValueError as ve:
            return jsonify({"message": str(ve)}), 400

        cur = mysql.connection.cursor(cursors.DictCursor)
        try:
          
            cur.execute(
                "SELECT activo FROM servicios WHERE id = %s AND id_usuario = %s",
                (id_servicio, id_user)
            )
            row = cur.fetchone()
            if not row or int(row["activo"]) != 1:
                return jsonify({"message": "Servicio no encontrado o inactivo"}), 404

            cur.execute(
                '''
                UPDATE servicios
                   SET nombre = %s, descripcion = %s, precio = %s
                 WHERE id = %s AND id_usuario = %s
                ''',
                (nombre, descripcion, precio, id_servicio, id_user)
            )
            mysql.connection.commit()
            return jsonify({
                "id": id_servicio,
                "nombre": nombre,
                "descripcion": descripcion,
                "precio": precio
            }), 200
        except Exception:
            mysql.connection.rollback()
            raise
        finally:
            cur.close()
    except Exception as e:
        return jsonify({"message": "Error interno"}), 500


@app.route('/usuarios/<int:id_user>/servicios/<int:id_servicio>', methods=['DELETE'])
@token_required
@user_resource_param("id_user")
@servicio_resource
def remove_servicios(id_user, id_servicio):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute(
            'UPDATE servicios SET activo = 0 WHERE id = %s AND id_usuario = %s',
            (id_servicio, id_user)
        )
        mysql.connection.commit()
        return jsonify({"message": "borrado lógico realizado", "id": id_servicio}), 200
    except Exception as e:
        return jsonify({"message": f"servicios:delete {str(e)}"}), 500
    finally:
        cur.close()


@app.route('/usuarios/<int:id_user>/servicios/<int:id_servicio>', methods=['GET'])
@token_required
@user_resource_param("id_user")
@servicio_resource
def get_servicio_by_id(id_user, id_servicio):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute(
            'SELECT * FROM servicios WHERE id = %s AND id_usuario = %s',
            (id_servicio, id_user)
        )
        row = cur.fetchone()
        if row:
            return jsonify(Servicio(row).to_json()), 200
        return jsonify({"message": "Servicio no encontrado"}), 404
    except Exception as e:
        return jsonify({"message": f"servicios:get-by-id {str(e)}"}), 500
    finally:
        cur.close()


@app.route('/usuarios/<int:id_user>/ranking-servicios', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_ranking_servicios(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        f_from, f_to = parse_from_to(request.args)

        params = [id_user]
        date_filter = ""
        if f_from and f_to:
            date_filter = " AND F.fecha_emision BETWEEN %s AND %s"
            params.extend([f_from, f_to])
        elif f_from:
            date_filter = " AND F.fecha_emision >= %s"
            params.append(f_from)
        elif f_to:
            date_filter = " AND F.fecha_emision <= %s"
            params.append(f_to)

        cur.execute(f'''
            SELECT S.nombre AS nombre_servicio,
                   COALESCE(SUM(DF.cantidad),0) AS cantidad_vendida
            FROM detalle_factura DF
            JOIN servicios S ON DF.id_servicio = S.id
            JOIN factura  F  ON DF.id_factura  = F.id
            WHERE F.id_usuario = %s
              AND DF.id_servicio IS NOT NULL
              {date_filter}
            GROUP BY DF.id_servicio, S.nombre
            ORDER BY cantidad_vendida DESC
            LIMIT 5
        ''', tuple(params))

        rows = cur.fetchall() or []
        if not rows:
            return jsonify({"message": "Sin servicios vendidos en el rango"}), 404

        resultados = [{
            "nombre_servicio": r["nombre_servicio"],
            "cantidad_vendida": float(r["cantidad_vendida"] or 0)
        } for r in rows]

        return jsonify(resultados), 200
    finally:
        cur.close()



@app.route('/usuarios/<int:id_user>/servicios/total', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_total_servicios(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute(
            'SELECT COUNT(*) AS total FROM servicios WHERE id_usuario = %s AND activo = 1',
            (id_user,)
        )
        row = cur.fetchone()
        total_servicios = int(row["total"] if row and row.get("total") is not None else 0)
        return jsonify({'total': total_servicios}), 200
    except Exception as e:
        return jsonify({"message": f"servicios:total {str(e)}"}), 500
    finally:
        cur.close()


@app.route('/usuarios/<int:id_user>/servicios-paginados', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_paginated_servicios(id_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 5
        if page < 1: page = 1
        if per_page < 1 or per_page > 100: per_page = 5
        offset = (page - 1) * per_page

        cur = mysql.connection.cursor(cursors.DictCursor)
        try:
            cur.execute(
                'SELECT COUNT(*) AS c FROM servicios WHERE id_usuario = %s AND activo = 1',
                (id_user,)
            )
            total_services = int(cur.fetchone()["c"])

            cur.execute('''
                SELECT * FROM servicios
                WHERE id_usuario = %s AND activo = 1
                ORDER BY id DESC
                LIMIT %s OFFSET %s
            ''', (id_user, per_page, offset))
            data = cur.fetchall() or []

            service_list = [Servicio(row).to_json() for row in data]
            total_pages = ceil(total_services / per_page) if per_page else 1

            return jsonify({
                "total_pages": total_pages,
                "current_page": page,
                "service": service_list
            }), 200
        finally:
            cur.close()
    except Exception as e:
        return jsonify({"message": f"servicios:paged {str(e)}"}), 500
