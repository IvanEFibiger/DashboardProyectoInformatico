from api.Utilidades import *
from flask import jsonify

"""Stock"""
"""Obtener los movimientos de stock"""
@app.route('/usuarios/<int:id_user>/stock_movimientos', methods=['GET'])
@token_required
@user_resources
def get_stock_movimientos(id_user):
    try:
        cur = mysql.connection.cursor()

        # Consulta para obtener el último movimiento de stock para cada producto del usuario
        cur.execute('''
            SELECT P.nombre as producto, MS.stock_real
            FROM productos P
            JOIN movimiento_stock MS ON P.id = MS.producto_id
            WHERE MS.id = (
                SELECT MAX(id)
                FROM movimiento_stock
                WHERE producto_id = P.id
            )
            AND P.id_usuario = %s
        ''', (id_user,))

        data = cur.fetchall()
        stock_movimientos = []

        for row in data:
            movimiento_info = {
                "producto": row[0],
                "stock_real": int(row[1])
            }

            stock_movimientos.append(movimiento_info)

        return jsonify(stock_movimientos)

    except Exception as e:
        return jsonify({"message": str(e)}), 500




@app.route('/usuarios/<int:id_user>/productos/<int:id_producto>/ultimo_stock', methods=['GET'])
@token_required
@user_resources
@producto_resource
def get_ultimo_stock_producto(id_user, id_producto):
    try:
        cur = mysql.connection.cursor()

        # Consulta para obtener el último movimiento de stock para un producto específico del usuario
        cur.execute('''
            SELECT MS.stock_real
            FROM movimiento_stock MS
            WHERE MS.producto_id = %s
            ORDER BY MS.id DESC
            LIMIT 1
        ''', (id_producto,))

        ultimo_stock = cur.fetchone()

        if ultimo_stock:
            return jsonify({"producto_id": id_producto, "stock_real": int(ultimo_stock[0])})
        else:
            return jsonify({"message": "No hay movimientos de stock para el producto"}), 404

    except Exception as e:
        return jsonify({"message": str(e)}), 500



"""Obtener el movimiento de stock por producto"""
@app.route('/usuarios/<int:id_user>/stock_movimientos/<int:id_producto>', methods=['GET'])
@token_required
@user_resources
@producto_resource
def get_stock_movimientos_by_producto(id_user, id_producto):  # Asegúrate de utilizar 'id_producto'
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT tipo, cantidad, fecha, stock_real FROM movimiento_stock WHERE producto_id = %s ORDER BY fecha', (id_producto,))

        data = cur.fetchall()
        stock_movimientos = []

        for row in data:
            movimiento_info = {
                "tipo": row[0],
                "cantidad": row[1],
                "fecha": row[2],
                "stock_real": int(row[3])
            }
            stock_movimientos.append(movimiento_info)

        return jsonify(stock_movimientos)

    except Exception as e:
        return jsonify({"message": str(e)}), 500


"""Obtener el historial de ventas"""
@app.route('/usuarios/<int:id_user>/historial_ventas', methods=['GET'])
@token_required
@user_resources
def get_historial_ventas(id_user):
    try:
        cur = mysql.connection.cursor()

        # Consulta para obtener el historial de ventas para cada producto del usuario
        cur.execute('''
            SELECT P.nombre as producto, DF.cantidad, F.fecha_emision
            FROM productos P
            JOIN detalle_factura DF ON P.id = DF.id_producto
            JOIN factura F ON DF.id_factura = F.id
            WHERE P.id_usuario = %s
        ''', (id_user,))

        data = cur.fetchall()
        historial_ventas = []

        for row in data:
            venta_info = {
                "producto": row[0],
                "cantidad": int(row[1]),
                "fecha_emision": row[2].strftime('%Y-%m-%d')  # Formatear la fecha a cadena
            }

            historial_ventas.append(venta_info)

        return jsonify(historial_ventas)

    except Exception as e:
        return jsonify({"message": str(e)}), 500