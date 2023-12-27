from api.models.Productos import Producto
from api.Utilidades import *
from flask import request, jsonify
import datetime
from datetime import date
from math import ceil

"""Productos"""

"""Obtener todos los productos"""
@app.route('/usuarios/<int:id_user>/productos', methods=['GET'])
@token_required
def get_all_productos(id_user):
   cur = mysql.connection.cursor()
   cur.execute('SELECT * FROM productos')
   data = cur.fetchall()
   prodList = []

   for row in data:
       objProd = Producto(row)
       prodList.append(objProd.to_json())

   return jsonify(prodList)


@app.route('/usuarios/<int:id_user>/productos/stock-positivo', methods=['GET'])
@token_required
@user_resources
def get_productos_con_stock_positivo(id_user):
    try:
        cur = mysql.connection.cursor()

        cur.execute('''
            SELECT P.*
            FROM productos P
            JOIN (
                SELECT MS.producto_id, MAX(MS.id) AS ultimo_id
                FROM movimiento_stock MS
                GROUP BY MS.producto_id
            ) ultimos_movimientos ON P.id = ultimos_movimientos.producto_id
            JOIN movimiento_stock MS ON P.id = MS.producto_id AND MS.id = ultimos_movimientos.ultimo_id
            WHERE MS.stock_real > 0
            AND P.id_usuario = %s  
        ''', (id_user,))

        data = cur.fetchall()
        prodList = []

        for row in data:
            objProd = Producto(row)
            prodList.append(objProd.to_json())

        return jsonify(prodList)

    except Exception as e:
        return jsonify({"message": str(e)}), 500


"""Crear nuevo producto"""
@app.route('/usuarios/<int:id_user>/productos', methods=['POST'])
@token_required
@user_resources
def create_producto(id_user):
    try:
        nombre = request.get_json()["nombre"]
        descripcion = request.get_json()["descripcion"]
        precio = request.get_json()["precio"]
        cantidad = request.get_json()["cantidad"]
        id_usuario = request.get_json()["id_usuario"]

        cur = mysql.connection.cursor()

        # Verificar si el producto ya existe, ya sea activo o inactivo
        cur.execute("SELECT id, activo FROM productos WHERE nombre = %s", (nombre,))
        producto_existente = cur.fetchone()

        if producto_existente:
            producto_id = producto_existente[0]
            producto_activo = producto_existente[1]

            if producto_activo:
                return jsonify({"message": "Producto ya registrado"})
            else:
                # Reactivar el producto
                cur.execute("UPDATE productos SET activo = 1 WHERE id = %s", (producto_id,))
                mysql.connection.commit()

                return jsonify({"message": "Producto reactivado", "id": producto_id})

        # Agregar el producto a la tabla productos
        cur.execute(
            'INSERT INTO productos (nombre, descripcion, precio, cantidad, id_usuario) VALUES (%s, %s, %s, %s, %s)',
            (nombre, descripcion, precio, cantidad, id_usuario))
        mysql.connection.commit()

        # Obtener el ID del registro creado
        cur.execute('SELECT LAST_INSERT_ID()')
        row = cur.fetchone()

        if row and row[0] is not None:
            producto_id = row[0]

            # Agregar el movimiento a la tabla movimiento_stock
            cur.execute(
                'INSERT INTO movimiento_stock (producto_id, tipo, cantidad, fecha, stock_real) VALUES (%s, %s, %s, %s, %s)',
                (producto_id, 'entrada', cantidad, date.today(), cantidad))
            mysql.connection.commit()

            return jsonify({
                "nombre": nombre,
                "descripcion": descripcion,
                "precio": precio,
                "cantidad": cantidad,
                "id_usuario": id_usuario,
                "id": producto_id
            })

        return jsonify({"message": "Error al obtener el ID del producto"}), 500

    except Exception as e:
        return jsonify({"message": str(e)}), 500


"""Modificar producto"""
@app.route('/usuarios/<int:id_user>/productos/<int:id_producto>', methods=['PUT'])
@token_required
@user_resources
@producto_resource
def update_producto(id_user, id_producto):  # Agregar id_user como parámetro
   nombre = request.get_json()["nombre"]
   descripcion = request.get_json()["descripcion"]
   precio = request.get_json()["precio"]
   cantidad = request.get_json()["cantidad"]

   cur = mysql.connection.cursor()
   cur.execute("UPDATE productos SET nombre = %s, descripcion = %s, precio = %s, cantidad = %s WHERE id = %s", (nombre, descripcion, precio, cantidad, id_producto))
   mysql.connection.commit()

   return jsonify({"id": id_producto, "nombre": nombre, "descripcion": descripcion, "precio": precio, "cantidad": cantidad})


"""modificar cantidad para control stock"""
@app.route('/usuarios/<int:id_user>/productos/<int:id_producto>/stock', methods=['PUT'])
@token_required
@user_resources
@producto_resource
def update_stock_producto(id_user, id_producto):
    try:
        nueva_cantidad = request.get_json()["cantidad"]

        cur = mysql.connection.cursor()

        # Verificar si el producto está activo
        cur.execute('SELECT activo FROM productos WHERE id = %s', (id_producto,))
        producto_activo = cur.fetchone()

        if not producto_activo or not producto_activo[0]:
            return jsonify({"message": "El producto no está activo"}), 400

        # Obtener el último valor de stock_real para ese producto
        cur.execute('SELECT stock_real FROM movimiento_stock WHERE producto_id = %s ORDER BY id DESC LIMIT 1', (id_producto,))
        ultimo_stock_real = cur.fetchone()

        # Calcular la nueva cantidad en stock_real
        nuevo_stock_real = nueva_cantidad if ultimo_stock_real is None else ultimo_stock_real[0] + nueva_cantidad

        # Actualizar stock_real en movimiento_stock
        cur.execute('INSERT INTO movimiento_stock (producto_id, tipo, cantidad, fecha, stock_real) VALUES (%s, %s, %s, %s, %s)', (id_producto, 'entrada', nueva_cantidad, datetime.now(), nuevo_stock_real))
        mysql.connection.commit()

        return jsonify({"message": "Cantidad actualizada"})
    except Exception as e:
        return jsonify({"message": str(e)}), 500


"""ELIMINAR Producto"""
@app.route('/usuarios/<int:id_user>/productos/<int:id_producto>', methods=['DELETE'])
@token_required
@user_resources
@producto_resource
def remove_producto(id_user, id_producto):
    try:
        cur = mysql.connection.cursor()

        # Realizar un borrado lógico actualizando la columna activo a 0
        cur.execute('UPDATE productos SET activo = 0 WHERE id = {0}'.format(id_producto))
        mysql.connection.commit()

        return jsonify({"message": "eliminado", "id": id_producto})

    except Exception as e:
        return jsonify({"message": str(e)}), 500


"""Consultar producto por id"""
@app.route('/usuarios/<int:id_user>/productos/<int:id_producto>', methods=['GET'])
@token_required
@user_resources
@producto_resource
def get_producto_by_id(id_user, id_producto):  # Cambiar el nombre del parámetro
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM productos WHERE id = %s', (id_producto,))
    data = cur.fetchall()

    if cur.rowcount > 0:
        objproducto = Producto(data[0])  # Asumiendo que tienes una clase Producto similar a la clase Clientes
        return jsonify(objproducto.to_json())

    return jsonify({"message": "ID no encontrado o producto sin stock"})



"""Obtener un ranking de los productos más vendidos"""
@app.route('/usuarios/<int:id_user>/ranking-productos', methods=['GET'])
@token_required
@user_resources
def get_ranking_productos(id_user):
    try:
        cur = mysql.connection.cursor()

        # Consultar el ranking de productos más vendidos para un usuario específico
        cur.execute('''
            SELECT P.nombre, SUM(DF.cantidad) as cantidad_vendida
            FROM detalle_factura DF
            JOIN productos P ON DF.id_producto = P.id
            JOIN factura F ON DF.id_factura = F.id
            WHERE F.id_usuario = %s
            GROUP BY DF.id_producto
            ORDER BY cantidad_vendida DESC
        ''', (id_user,))

        ranking_productos = cur.fetchall()

        if not ranking_productos:
            return jsonify({"message": "No hay productos vendidos para este usuario"}), 404

        # Crear una lista de resultados
        resultados = []

        for producto in ranking_productos:
            nombre_producto = producto[0]
            cantidad_vendida = producto[1]

            resultado = {
                "nombre_producto": nombre_producto,
                "cantidad_vendida": cantidad_vendida
            }

            resultados.append(resultado)

        return jsonify(resultados)

    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Endpoint para obtener el total de clientes
@app.route('/usuarios/<int:id_user>/productos/total', methods=['GET'])
@token_required
@user_resources
def get_total_productos(id_user):
    cur = mysql.connection.cursor()
    cur.execute('SELECT COUNT(*) FROM productos WHERE id_usuario = {0} AND activo = 1'.format(id_user))
    total_productos = cur.fetchone()[0]
    return jsonify({'total': total_productos})




@app.route('/usuarios/<int:id_user>/productos-paginados', methods=['GET'])
@token_required
@user_resources
def get_paginated_productos(id_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 5  # Número de productos por página

        cur = mysql.connection.cursor()
        cur.execute('SELECT COUNT(*) FROM productos WHERE id_usuario = %s AND activo = 1', (id_user,))
        total_products = cur.fetchone()[0]

        cur.execute('SELECT * FROM productos WHERE id_usuario = %s AND activo = 1 LIMIT %s OFFSET %s', (id_user, per_page, (page - 1) * per_page))
        print(cur.mogrify('SELECT * FROM productos WHERE id_usuario = %s AND activo = 1 LIMIT %s OFFSET %s',
                          (id_user, per_page, (page - 1) * per_page)))
        data = cur.fetchall()

        productList = []

        for row in data:
            objProductos = Producto(row)
            productList.append(objProductos.to_json())

        total_pages = ceil(total_products / per_page)
        current_page = page

        response_data = {
            "total_pages": total_pages,
            "current_page": current_page,
            "Products": productList
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"message": str(e)}), 500

