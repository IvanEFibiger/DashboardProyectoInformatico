# api/routes/movimiento_stock.py
from api import app
from api.Utilidades import token_required, user_resource_param, producto_resource
from flask import jsonify
from api.db.db import mysql
import MySQLdb.cursors as cursors
from datetime import datetime


@app.route('/usuarios/<int:id_user>/stock_movimientos', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_stock_movimientos(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute('''
            SELECT P.nombre AS producto, MS.stock_real
            FROM productos P
            JOIN movimiento_stock MS ON P.id = MS.producto_id
            WHERE P.id_usuario = %s
              AND MS.id = (
                  SELECT MAX(id)
                  FROM movimiento_stock
                  WHERE producto_id = P.id
              )
              AND P.activo = 1
        ''', (id_user,))
        rows = cur.fetchall() or []
        stock_movimientos = [{
            "producto": r["producto"],
            "stock_real": int(r["stock_real"] or 0)
        } for r in rows]
        return jsonify(stock_movimientos), 200
    except Exception as e:
        return jsonify({"message": f"stock:list {str(e)}"}), 500
    finally:
        cur.close()


@app.route('/usuarios/<int:id_user>/productos/<int:id_producto>/ultimo_stock', methods=['GET'])
@token_required
@user_resource_param("id_user")
@producto_resource
def get_ultimo_stock_producto(id_user, id_producto):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute('''
            SELECT stock_real
            FROM movimiento_stock
            WHERE producto_id = %s
            ORDER BY id DESC
            LIMIT 1
        ''', (id_producto,))
        row = cur.fetchone()

        if row and row.get("stock_real") is not None:
            return jsonify({"producto_id": id_producto, "stock_real": int(row["stock_real"])}), 200
        else:
            return jsonify({"message": "No hay movimientos de stock para el producto"}), 404
    except Exception as e:
        return jsonify({"message": f"stock:last {str(e)}"}), 500
    finally:
        cur.close()


@app.route('/usuarios/<int:id_user>/stock_movimientos/<int:id_producto>', methods=['GET'])
@token_required
@user_resource_param("id_user")
@producto_resource
def get_stock_movimientos_by_producto(id_user, id_producto):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute('''
            SELECT tipo, cantidad, fecha, stock_real
            FROM movimiento_stock
            WHERE producto_id = %s
            ORDER BY fecha, id
        ''', (id_producto,))
        rows = cur.fetchall() or []

        def _fmt_fecha(f):
            if isinstance(f, datetime):
                return f.strftime('%Y-%m-%d %H:%M:%S')
            return f

        stock_movimientos = [{
            "tipo": r["tipo"],
            "cantidad": float(r["cantidad"]),
            "fecha": _fmt_fecha(r["fecha"]),
            "stock_real": int(r["stock_real"] or 0)
        } for r in rows]

        return jsonify(stock_movimientos), 200
    except Exception as e:
        return jsonify({"message": f"stock:history {str(e)}"}), 500
    finally:
        cur.close()


@app.route('/usuarios/<int:id_user>/historial_ventas', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_historial_ventas(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute('''
            SELECT P.nombre AS producto, DF.cantidad, F.fecha_emision
            FROM productos P
            JOIN detalle_factura DF ON P.id = DF.id_producto
            JOIN factura F ON DF.id_factura = F.id
            WHERE P.id_usuario = %s
            ORDER BY F.fecha_emision, F.id, DF.id
        ''', (id_user,))
        rows = cur.fetchall() or []

        def _fmt_fecha(f):
            if isinstance(f, datetime):
                return f.strftime('%Y-%m-%d')
            return f

        historial_ventas = [{
            "producto": r["producto"],
            "cantidad": float(r["cantidad"]),
            "fecha_emision": _fmt_fecha(r["fecha_emision"])
        } for r in rows]

        return jsonify(historial_ventas), 200
    except Exception as e:
        return jsonify({"message": f"ventas:history {str(e)}"}), 500
    finally:
        cur.close()
