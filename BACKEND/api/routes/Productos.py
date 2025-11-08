# api/routes/routes_productos.py
from api import app
from api.models.Productos import Producto
from api.Utilidades import token_required, user_resource_param, producto_resource
from api.db.db import mysql
from flask import request, jsonify
from datetime import date  
from math import ceil
import MySQLdb.cursors as cursors
from api.utils.date_range import parse_from_to




def _producto_con_stock_actual(row):

    if isinstance(row, dict):
        stock_actual = row.get("stock_actual", 0) or 0
        prod = Producto(row).to_json()
    else:
        r = list(row)
        stock_actual = r[7] if len(r) >= 8 and r[7] is not None else 0
        prod = Producto(r).to_json()

    try:
        prod["cantidad"] = int(stock_actual)
    except Exception:
        prod["cantidad"] = 0
    return prod

def _require_number(value, name):
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} inválido")

def _require_non_negative_int(value, name):

    try:
        iv = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} debe ser entero")
    if iv < 0:
        raise ValueError(f"{name} no puede ser negativo")
    return iv

def _require_positive_int(value, name):
    try:
        iv = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} debe ser entero")
    if iv <= 0:
        raise ValueError(f"{name} debe ser > 0")
    return iv


@app.route('/usuarios/<int:id_user>/productos', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_all_productos(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute("""
            SELECT * FROM v_stock_actual
            WHERE id_usuario = %s AND activo = 1
            ORDER BY id DESC
        """, (id_user,))
        data = cur.fetchall() or []
        prod_list = [_producto_con_stock_actual(row) for row in data]
        return jsonify(prod_list), 200
    except Exception as e:
        return jsonify({"message": f"productos:list {str(e)}"}), 500
    finally:
        cur.close()


@app.route('/usuarios/<int:id_user>/productos/stock-positivo', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_productos_con_stock_positivo(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute('''
            SELECT P.id
            FROM productos P
            JOIN (
                SELECT MS.producto_id, MAX(MS.id) AS ultimo_id
                FROM movimiento_stock MS
                GROUP BY MS.producto_id
            ) ult ON P.id = ult.producto_id
            JOIN movimiento_stock MS ON MS.id = ult.ultimo_id
            WHERE MS.stock_real > 0
              AND P.id_usuario = %s
              AND P.activo = 1
        ''', (id_user,))
        ids_rows = cur.fetchall() or []
        ids = [r["id"] for r in ids_rows]
        if not ids:
            return jsonify([]), 200

        fmt = ','.join(['%s'] * len(ids))
        cur.execute(f"SELECT * FROM v_stock_actual WHERE id IN ({fmt})", tuple(ids))
        vs_rows = cur.fetchall() or []
        vs = {r["id"]: _producto_con_stock_actual(r) for r in vs_rows}
        out = [vs[i] for i in ids if i in vs]
        return jsonify(out), 200
    except Exception as e:
        return jsonify({"message": f"productos:stock-positivo {str(e)}"}), 500
    finally:
        cur.close()


@app.route('/usuarios/<int:id_user>/productos', methods=['POST'])
@token_required
@user_resource_param("id_user")
def create_producto(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        body = request.get_json(force=True) or {}
        nombre      = (body.get("nombre") or "").strip()
        descripcion = (body.get("descripcion") or "").strip()
        precio_raw  = body.get("precio")
        cantidad_raw= body.get("cantidad")  

        if not nombre or precio_raw is None or cantidad_raw is None:
            return jsonify({"message": "nombre, precio y cantidad son obligatorios"}), 400

       
        try:
            precio = _require_number(precio_raw, "precio")
            if precio < 0:
                return jsonify({"message": "precio no puede ser negativo"}), 400
            cantidad = _require_non_negative_int(cantidad_raw, "cantidad")
        except ValueError as ve:
            return jsonify({"message": str(ve)}), 400

       
        cur.execute(
            "SELECT id, activo FROM productos WHERE nombre = %s AND id_usuario = %s",
            (nombre, id_user)
        )
        prod = cur.fetchone()

        if prod:
            prod_id = int(prod["id"])
            activo = int(prod["activo"])
            if activo == 1:
                return jsonify({"message": "Producto ya registrado"}), 409

       
            cur.execute("UPDATE productos SET activo = 1, precio = %s WHERE id = %s", (precio, prod_id))
            mysql.connection.commit()

          
            cur.execute(
                'INSERT INTO movimiento_stock (producto_id, tipo, cantidad, fecha, stock_real) '
                'VALUES (%s, %s, %s, %s, %s)',
                (prod_id, 'entrada', cantidad, date.today(), cantidad)
            )
            mysql.connection.commit()
            return jsonify({"message": "Producto reactivado", "id": prod_id}), 200

     
        cur.execute(
            'INSERT INTO productos (nombre, descripcion, precio, cantidad, id_usuario, activo) '
            'VALUES (%s, %s, %s, %s, %s, 1)',
            (nombre, descripcion, precio, cantidad, id_user)
        )
        mysql.connection.commit()

        producto_id = cur.lastrowid
        if not producto_id:
            return jsonify({"message": "No se obtuvo ID del producto"}), 500


        cur.execute(
            'INSERT INTO movimiento_stock (producto_id, tipo, cantidad, fecha, stock_real) '
            'VALUES (%s, %s, %s, %s, %s)',
            (producto_id, 'entrada', cantidad, date.today(), cantidad)
        )
        mysql.connection.commit()

     
        cur.execute("SELECT * FROM v_stock_actual WHERE id = %s", (producto_id,))
        vs = cur.fetchone()
        return jsonify(_producto_con_stock_actual(vs)), 201
    except Exception as e:
        return jsonify({"message": f"productos:create {str(e)}"}), 500
    finally:
        cur.close()


@app.route('/usuarios/<int:id_user>/productos/<int:id_producto>', methods=['PUT'])
@token_required
@user_resource_param("id_user")
@producto_resource
def update_producto(id_user, id_producto):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        body = request.get_json(force=True) or {}
        nombre      = (body.get("nombre") or "").strip()
        descripcion = (body.get("descripcion") or "").strip()
        precio_raw  = body.get("precio")

        if not nombre or precio_raw is None:
            return jsonify({"message": "nombre y precio son obligatorios"}), 400

        try:
            precio = _require_number(precio_raw, "precio")
            if precio < 0:
                return jsonify({"message": "precio no puede ser negativo"}), 400
        except ValueError as ve:
            return jsonify({"message": str(ve)}), 400

        cur.execute(
            "UPDATE productos SET nombre = %s, descripcion = %s, precio = %s "
            "WHERE id = %s AND id_usuario = %s",
            (nombre, descripcion, precio, id_producto, id_user)
        )
        mysql.connection.commit()

        cur.execute(
            "SELECT * FROM v_stock_actual WHERE id = %s AND id_usuario = %s",
            (id_producto, id_user)
        )
        row = cur.fetchone()
        if not row:
            return jsonify({"message": "Producto no encontrado"}), 404
        return jsonify(_producto_con_stock_actual(row)), 200
    except Exception as e:
        return jsonify({"message": f"productos:update {str(e)}"}), 500
    finally:
        cur.close()


@app.route('/usuarios/<int:id_user>/productos/<int:id_producto>/stock', methods=['PUT'])
@token_required
@user_resource_param("id_user")
@producto_resource
def update_stock_producto(id_user, id_producto):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        body = request.get_json(force=True) or {}
        cantidad_raw = body.get("cantidad")
        if cantidad_raw is None:
            return jsonify({"message": "cantidad es obligatoria"}), 400

      
        try:
            cantidad = _require_positive_int(cantidad_raw, "cantidad")
        except ValueError as ve:
            return jsonify({"message": str(ve)}), 400


        cur.execute(
            'SELECT activo FROM productos WHERE id = %s AND id_usuario = %s',
            (id_producto, id_user)
        )
        row = cur.fetchone()
        if not row or int(row["activo"]) != 1:
            return jsonify({"message": "El producto no está activo"}), 400

 
        cur.execute(
            'SELECT stock_real FROM movimiento_stock WHERE producto_id = %s ORDER BY id DESC LIMIT 1 FOR UPDATE',
            (id_producto,)
        )
        last = cur.fetchone()
        last_stock = int(last["stock_real"]) if last and last.get("stock_real") is not None else 0

        nuevo_stock_real = last_stock + cantidad  

        cur.execute(
            'INSERT INTO movimiento_stock (producto_id, tipo, cantidad, fecha, stock_real) '
            'VALUES (%s, %s, %s, %s, %s)',
            (id_producto, 'entrada', cantidad, date.today(), nuevo_stock_real)
        )
        mysql.connection.commit()

        return jsonify({"message": "Stock actualizado", "stock_real": nuevo_stock_real}), 200
    except Exception as e:
        return jsonify({"message": f"productos:update-stock {str(e)}"}), 500
    finally:
        cur.close()


@app.route('/usuarios/<int:id_user>/productos/<int:id_producto>', methods=['DELETE'])
@token_required
@user_resource_param("id_user")
@producto_resource
def remove_producto(id_user, id_producto):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute(
            'UPDATE productos SET activo = 0 WHERE id = %s AND id_usuario = %s',
            (id_producto, id_user)
        )
        mysql.connection.commit()
        return jsonify({"message": "eliminado", "id": id_producto}), 200
    except Exception as e:
        return jsonify({"message": f"productos:delete {str(e)}"}), 500
    finally:
        cur.close()


@app.route('/usuarios/<int:id_user>/productos/<int:id_producto>', methods=['GET'])
@token_required
@user_resource_param("id_user")
@producto_resource
def get_producto_by_id(id_user, id_producto):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute(
            'SELECT * FROM v_stock_actual WHERE id = %s AND id_usuario = %s',
            (id_producto, id_user)
        )
        row = cur.fetchone()
        if row:
            return jsonify(_producto_con_stock_actual(row)), 200
        return jsonify({"message": "ID no encontrado"}), 404
    except Exception as e:
        return jsonify({"message": f"productos:get-by-id {str(e)}"}), 500
    finally:
        cur.close()


@app.route('/usuarios/<int:id_user>/ranking-productos', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_ranking_productos(id_user):
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
            SELECT P.nombre AS nombre_producto, COALESCE(SUM(DF.cantidad),0) AS cantidad_vendida
            FROM detalle_factura DF
            JOIN productos P ON DF.id_producto = P.id
            JOIN factura  F  ON DF.id_factura  = F.id
            WHERE F.id_usuario = %s AND DF.id_producto IS NOT NULL {date_filter}
            GROUP BY DF.id_producto, P.nombre
            ORDER BY cantidad_vendida DESC
        ''', tuple(params))
        rows = cur.fetchall() or []
        if not rows:
            return jsonify([]), 200
        return jsonify([{
            "nombre_producto": r["nombre_producto"],
            "cantidad_vendida": float(r["cantidad_vendida"] or 0)
        } for r in rows]), 200
    finally:
        cur.close()



@app.route('/usuarios/<int:id_user>/productos/total', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_total_productos(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute(
            'SELECT COUNT(*) AS total FROM productos WHERE id_usuario = %s AND activo = 1',
            (id_user,)
        )
        row = cur.fetchone()
        total_productos = int(row["total"] if row and row.get("total") is not None else 0)
        return jsonify({'total': total_productos}), 200
    except Exception as e:
        return jsonify({"message": f"productos:total {str(e)}"}), 500
    finally:
        cur.close()


@app.route('/usuarios/<int:id_user>/productos-paginados', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_paginated_productos(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 5
        if page < 1: page = 1
        if per_page < 1 or per_page > 100: per_page = 5
        offset = (page - 1) * per_page

        cur.execute(
            'SELECT COUNT(*) AS total FROM productos WHERE id_usuario = %s AND activo = 1',
            (id_user,)
        )
        row = cur.fetchone()
        total_products = int(row["total"] if row and row.get("total") is not None else 0)

        cur.execute(
            'SELECT * FROM v_stock_actual WHERE id_usuario = %s AND activo = 1 '
            'ORDER BY id DESC LIMIT %s OFFSET %s',
            (id_user, per_page, offset)
        )
        data = cur.fetchall() or []

        product_list = [_producto_con_stock_actual(r) for r in data]
        total_pages = ceil(total_products / per_page) if per_page else 1

        return jsonify({
            "total_pages": total_pages,
            "current_page": page,
            "products": product_list
        }), 200
    except Exception as e:
        return jsonify({"message": f"productos:paged {str(e)}"}), 500
    finally:
        cur.close()
