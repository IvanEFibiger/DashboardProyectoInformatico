from api.models.factura import Factura
from api.models.Productos import Producto
from api.models.Servicios import Servicio
from api.models.detalle_factura import DetalleFactura
from api.Utilidades import *
from flask import request, jsonify
from api.db.db import mysql
from  math import ceil
"""factura"""

"Obtener todas las facturas"
@app.route('/usuarios/<int:id_user>/factura', methods=['GET'])
@token_required
@user_resources
def get_all_facturas(id_user):
   cur = mysql.connection.cursor()
   cur.execute('SELECT * FROM factura')
   data = cur.fetchall()
   facturaList = []

   for row in data:
       objFactura = Factura(row)
       facturaList.append(objFactura.to_json())

   return jsonify(facturaList)




@app.route('/usuarios/<int:id_user>/factura', methods=['POST'])
@token_required
@user_resources
def create_factura(id_user):
    try:
        fecha_emision = request.get_json()["fecha_emision"]
        id_clientes = request.get_json()["id_clientes"]
        id_usuario = request.get_json()["id_usuario"]
        productos_servicios = request.get_json()["productos_servicios"]

        cur = mysql.connection.cursor()

        # Guardar la factura
        cur.execute('INSERT INTO Factura (fecha_emision, id_clientes, id_usuario) VALUES (%s, %s, %s)',
                    (fecha_emision, id_clientes, id_usuario))
        mysql.connection.commit()

        # Obtener el ID de la factura recién creada
        cur.execute('SELECT LAST_INSERT_ID()')
        row = cur.fetchone()

        if row and row[0] is not None:
            factura_id = row[0]

            # Guardar los detalles de la factura
            for producto_servicio in productos_servicios:
                cantidad = producto_servicio["cantidad"]
                id_producto = producto_servicio.get("id_producto")
                id_servicio = producto_servicio.get("id_servicio")



                # Obtener la fecha de la factura
                fecha_factura = fecha_emision

                # Obtener el precio del producto o servicio
                if id_producto:
                    cur.execute('SELECT precio FROM productos WHERE id = %s', (id_producto,))
                elif id_servicio:
                    cur.execute('SELECT precio FROM servicios WHERE id = %s', (id_servicio,))

                precio_unitario_row = cur.fetchone()

                if precio_unitario_row and precio_unitario_row[0] is not None:
                    precio_unitario = precio_unitario_row[0]
                    subtotal = cantidad * precio_unitario

                    # Guardar un detalle de la factura por cada producto o servicio
                    cur.execute(
                        'INSERT INTO Detalle_factura (id_factura, id_producto, id_servicio, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s, %s)',
                        (factura_id, id_producto, id_servicio, cantidad, precio_unitario, subtotal))
                    mysql.connection.commit()

                    # Actualizar el control de stock para el producto si id_producto no es nulo
                    if id_producto:
                        # Obtener el último stock real del producto
                        cur.execute(
                            'SELECT stock_real FROM movimiento_stock WHERE producto_id = %s ORDER BY id DESC LIMIT 1',
                            (id_producto,))
                        last_stock_row = cur.fetchone()

                        if last_stock_row and last_stock_row[0] is not None:
                            last_stock_real = last_stock_row[0]
                            new_stock_real = last_stock_real - cantidad

                            # Insertar un nuevo movimiento de stock con la salida
                            cur.execute(
                                'INSERT INTO movimiento_stock (producto_id, tipo, cantidad, fecha, stock_real) VALUES (%s, %s, %s, %s, %s)',
                                (id_producto, 'salida', cantidad, fecha_factura, new_stock_real))
                            mysql.connection.commit()
                        else:
                            return jsonify({
                                "message": f"No se encontró el último stock para el producto con ID {id_producto}"}), 500

                else:
                    return jsonify(
                        {
                            "message": f"No se encontró el precio para el {'producto' if id_producto else 'servicio'} con ID {id_producto or id_servicio}"}), 500



            # Calcular y actualizar la columna total
            cur.execute('SELECT SUM(subtotal) FROM Detalle_factura WHERE id_factura = %s', (factura_id,))
            total_row = cur.fetchone()

            if total_row and total_row[0] is not None:
                total = total_row[0]

                # Actualizar la columna total en la tabla Factura
                cur.execute('UPDATE Factura SET total = %s WHERE id = %s', (total, factura_id))
                mysql.connection.commit()

                return jsonify({"factura_id": factura_id})
            else:
                return jsonify({"message": "Error al calcular el total de la factura"}), 500

        else:
            return jsonify({"message": "Error al obtener el ID de la factura"}), 500

    except Exception as e:
        return jsonify({"message": str(e)}), 500


"""Actualizar factura por id"""
@app.route('/usuarios/<int:id_user>/factura/<int:id_factura>', methods=['PUT'])
@token_required
@user_resources
@factura_resource
def update_factura(id_user, id_factura):  # Agregar 'id_user' como parámetro
    fecha_emision = request.get_json()["fecha_emision"]
    id_clientes = request.get_json()["id_clientes"]

    cur = mysql.connection.cursor()
    cur.execute("UPDATE factura SET fecha_emision = %s, id_clientes = %s, id_usuario = %s WHERE id = %s",
                (fecha_emision, id_clientes, id_user, id_factura))
    mysql.connection.commit()

    return jsonify({"factura_id": id_factura, "fecha_emision": fecha_emision, "id_clientes": id_clientes})


"""Eliminar factura por id"""
@app.route('/usuarios/<int:id_user>/factura/<int:id_factura>', methods=['DELETE'])
@token_required
@user_resources
@factura_resource
def remove_factura(id_user, id_factura):  # Asegúrate de utilizar 'id_user' y 'id_factura'
    try:
        cur = mysql.connection.cursor()

        # Eliminar detalles de la factura
        cur.execute('DELETE FROM Detalle_factura WHERE id_factura = %s', (id_factura,))
        mysql.connection.commit()

        # Eliminar la factura
        cur.execute('DELETE FROM Factura WHERE id = %s', (id_factura,))
        mysql.connection.commit()

        return jsonify({"message": "Factura eliminada", "factura_id": id_factura})

    except Exception as e:
        return jsonify({"message": str(e)}), 500


"""Consultar factura completa por id"""
@app.route('/usuarios/<int:id_user>/factura/<int:id_factura>', methods=['GET'])
@token_required
@user_resources
@factura_resource
def consultar_factura(id_user, id_factura):
    cur = mysql.connection.cursor()

    # Consultar factura y detalles por ID
    cur.execute('''
        SELECT
            factura.*,
            clientes.nombre,
            clientes.cuit
        FROM factura
        INNER JOIN clientes ON factura.id_clientes = Clientes.id
        WHERE factura.id = %s
    ''', (id_factura,))

    data_factura = cur.fetchall()

    if cur.rowcount == 0:
        return jsonify({"message": "Factura no encontrada"}), 404

    obj_factura = Factura(data_factura[0])
    factura_info = obj_factura.to_json()

    # Calcular el total de la factura
    cur.execute('SELECT total FROM factura WHERE id = %s', (id_factura,))
    total_row = cur.fetchone()
    total = total_row[0] if total_row and total_row[0] is not None else 0

    # Consultar detalle de factura por ID de factura
    cur.execute('SELECT * FROM detalle_factura WHERE id_factura = %s', (id_factura,))
    data_detalle = cur.fetchall()

    detalle_list = []
    for row in data_detalle:
        obj_detalle = DetalleFactura(row)
        detalle_list.append(obj_detalle.to_json())

    # Consultar productos y servicios asociados al detalle de factura
    productos_servicios_list = []
    for detalle in detalle_list:
        if detalle["id_producto"]:
            cur.execute('SELECT * FROM productos WHERE id = %s', (detalle["id_producto"],))
            data_producto = cur.fetchone()
            obj_producto = Producto(data_producto)
            productos_servicios_list.append(obj_producto.to_json())
        elif detalle["id_servicio"]:
            cur.execute('SELECT * FROM servicios WHERE id = %s', (detalle["id_servicio"],))
            data_servicio = cur.fetchone()
            obj_servicio = Servicio(data_servicio)
            productos_servicios_list.append(obj_servicio.to_json())

    # Organizar la salida
    output = {
        "factura": factura_info,
        "cliente": {
            "nombre_cliente": data_factura[0][5],  # Usando el índice correcto para 'nombre'
            "cuit_cliente": data_factura[0][6]  # Usando el índice correcto para 'cuit'
        },
        "detalles": detalle_list,
        "productos_servicios": productos_servicios_list,
        "total": total
    }

    return jsonify(output)




@app.route('/usuarios/<int:id_user>/factura/total', methods=['GET'])
@token_required
@user_resources
def get_total_facturas(id_user):
    try:
        cur = mysql.connection.cursor()

        # Consultar todos los totales de las facturas para el usuario específico
        cur.execute('SELECT total FROM Factura WHERE id_usuario = %s', (id_user,))
        total_rows = cur.fetchall()

        if not total_rows:
            return jsonify({"message": f"No hay facturas para el usuario con ID {id_user}"}), 404

        # Calcular el valor total sumando todos los totales
        total_value = sum(row[0] for row in total_rows)

        return jsonify({"total_facturas_usuario": total_value})

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/usuarios/<int:id_user>/factura/cantidad', methods=['GET'])
@token_required
@user_resources
def get_cantidad_facturas(id_user):
    try:
        cur = mysql.connection.cursor()

        # Contar la cantidad de facturas para el usuario específico
        cur.execute('SELECT COUNT(*) FROM Factura WHERE id_usuario = %s', (id_user,))
        cantidad_facturas = cur.fetchone()[0]

        return jsonify({"cantidad_facturas_usuario": cantidad_facturas})

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route('/usuarios/<int:id_user>/factura/producto-mas-vendido', methods=['GET'])
@token_required
@user_resources
def get_producto_mas_vendido(id_user):
    try:
        cur = mysql.connection.cursor()

        # Consultar los productos más vendidos para el usuario específico
        cur.execute('''
            SELECT P.nombre, SUM(DF.id_producto) as cantidad_vendida
            FROM detalle_factura DF
            JOIN productos P ON DF.id_producto = P.id
            JOIN factura F ON DF.id_factura = F.id
            WHERE F.id_usuario = %s
            GROUP BY DF.id_producto
            ORDER BY cantidad_vendida DESC
            LIMIT 1
        ''', (id_user,))

        producto_mas_vendido = cur.fetchone()

        if not producto_mas_vendido:
            return jsonify({"message": f"No hay productos vendidos para el usuario con ID {id_user}"}), 404

        nombre_producto = producto_mas_vendido[0]
        cantidad_vendida = producto_mas_vendido[1]

        return jsonify({"producto_mas_vendido": nombre_producto, "cantidad_vendida": cantidad_vendida})

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route('/usuarios/<int:id_user>/factura/servicio-mas-vendido', methods=['GET'])
@token_required
@user_resources
def get_servicio_mas_vendido(id_user):
    try:
        cur = mysql.connection.cursor()

        # Consultar el servicio más vendido para el usuario específico
        cur.execute('''
            SELECT S.nombre, SUM(DF.cantidad) as cantidad_vendida
            FROM detalle_factura DF
            JOIN servicios S ON DF.id_servicio = S.id
            JOIN factura F ON DF.id_factura = F.id
            WHERE F.id_usuario = %s
            GROUP BY DF.id_servicio
            ORDER BY cantidad_vendida DESC
            LIMIT 1
        ''', (id_user,))

        servicio_mas_vendido = cur.fetchone()

        if not servicio_mas_vendido:
            return jsonify({"message": f"No hay servicios vendidos para el usuario con ID {id_user}"}), 404

        nombre_servicio = servicio_mas_vendido[0]
        cantidad_vendida = servicio_mas_vendido[1]

        return jsonify({"servicio_mas_vendido": nombre_servicio, "cantidad_vendida": cantidad_vendida})

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route('/usuarios/<int:id_user>/facturas/total', methods=['GET'])
@token_required
@user_resources
def get_total_facturas_creadas(id_user):
    try:
        cur = mysql.connection.cursor()

        # Contar la cantidad de facturas para el usuario específico
        cur.execute('SELECT COUNT(*) FROM Factura WHERE id_usuario = %s', (id_user,))
        total_facturas = cur.fetchone()[0]

        return jsonify({"total_facturas_creadas": total_facturas})

    except Exception as e:
        return jsonify({"message": str(e)}), 500



@app.route('/usuarios/<int:id_user>/facturas/detalles', methods=['GET'])
@token_required
@user_resources
def get_detalles_facturas_paginadas(id_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 5  # Número de facturas por página

        cur = mysql.connection.cursor()

        # Consultar todas las facturas para el usuario específico
        cur.execute('SELECT * FROM factura WHERE id_usuario = %s', (id_user,))
        data_facturas = cur.fetchall()

        if not data_facturas:
            return jsonify({"message": f"No hay facturas para el usuario con ID {id_user}"}), 404

        total_facturas = len(data_facturas)

        # Calcular el rango de facturas para la página actual
        start_index = (page - 1) * per_page
        end_index = start_index + per_page

        # Filtrar las facturas para la página actual
        facturas_paginadas = data_facturas[start_index:end_index]

        factura_list = []

        for factura_data in facturas_paginadas:
            factura_id = factura_data[0]
            fecha_emision = factura_data[1]
            id_cliente = factura_data[2]

            # Obtener el nombre del cliente
            cur.execute('SELECT nombre FROM clientes WHERE id = %s', (id_cliente,))
            nombre_cliente = cur.fetchone()[0]  # Asegúrate de seleccionar el primer elemento de la tupla

            total = factura_data[4]

            factura_info = {
                "factura_id": factura_id,
                "fecha_emision": fecha_emision,
                "nombre_cliente": nombre_cliente,
                "total": total
            }

            factura_list.append(factura_info)

        total_pages = ceil(total_facturas / per_page)
        current_page = page

        response_data = {
            "total_pages": total_pages,
            "current_page": current_page,
            "facturas_detalles": factura_list
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"message": str(e)}), 500
