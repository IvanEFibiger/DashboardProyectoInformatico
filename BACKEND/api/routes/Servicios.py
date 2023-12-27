from api.models.Servicios import Servicio
from api.Utilidades import *
from flask import request, jsonify
from math import ceil

"""servicios"""

"""Obtener todos los servicios activos"""
@app.route('/usuarios/<int:id_user>/servicios', methods=['GET'])
@token_required
@user_resources
def get_all_servicios(id_user):
    cur = mysql.connection.cursor()

    # Modificar la consulta para obtener solo servicios activos
    cur.execute('SELECT * FROM servicios WHERE activo = 1')

    data = cur.fetchall()
    servList = []

    for row in data:
        objServ = Servicio(row)
        servList.append(objServ.to_json())

    return jsonify(servList)

"""Crear nuevo servicio"""
@app.route('/usuarios/<int:id_user>/servicios', methods=['POST'])
@token_required
@user_resources
def create_servicio(id_user):
    try:
        nombre = request.get_json()["nombre"]
        descripcion = request.get_json()["descripcion"]
        precio = request.get_json()["precio"]

        cur = mysql.connection.cursor()

        # Verificar si el servicio ya existe (activo o inactivo)
        cur.execute("SELECT * FROM servicios WHERE nombre = %s", (nombre,))
        row = cur.fetchone()

        if row:
            # Si el servicio existe, verificar si está inactivo y reactivarlo
            if not row["activo"]:
                cur.execute("UPDATE servicios SET activo = 1 WHERE id = %s", (row["id"],))
                mysql.connection.commit()
                return jsonify({"message": "Servicio reactivado", "id": row["id"]})

            return jsonify({"message": "Servicio ya registrado", "id": row["id"]})

        # Agregar el servicio a la tabla servicios
        cur.execute('INSERT INTO servicios (nombre, descripcion, precio, id_usuario) VALUES (%s, %s, %s, %s)',
                    (nombre, descripcion, precio, id_user))
        mysql.connection.commit()

        # Obtener el ID del registro creado
        cur.execute('SELECT LAST_INSERT_ID()')
        row = cur.fetchone()
        id_servicio = row[0]

        return jsonify({"nombre": nombre, "descripcion": descripcion, "precio": precio, "id_usuario": id_user,
                        "id": id_servicio})
    except Exception as e:
        return jsonify({"message": str(e)}), 500  # Devolver un mensaje de error y código 500 en caso de excepción


"""Modificar servicio"""
@app.route('/usuarios/<int:id_user>/servicios/<int:id_servicio>', methods=['PUT'])
@token_required
@user_resources
@servicio_resource
def update_servicio(id_user, id_servicio):  # Agregar id_user e id_servicio como parámetros
    try:
        nombre = request.get_json()["nombre"]
        descripcion = request.get_json()["descripcion"]
        precio = request.get_json()["precio"]

        cur = mysql.connection.cursor()

        # Verificar si el servicio existe y está activo
        cur.execute("SELECT * FROM servicios WHERE id = %s AND activo = 1", (id_servicio,))
        row = cur.fetchone()

        if not row:
            return jsonify({"message": "Servicio no encontrado o inactivo"}), 404

        # Actualizar el servicio en la tabla servicios
        cur.execute("UPDATE servicios SET nombre = %s, descripcion = %s, precio = %s WHERE id = %s",
                    (nombre, descripcion, precio, id_servicio))
        mysql.connection.commit()

        return jsonify({"id": id_servicio, "nombre": nombre, "descripcion": descripcion, "precio": precio})
    except Exception as e:
        return jsonify({"message": str(e)}), 500  # Devolver un mensaje de error y código 500 en caso de excepción


"""Borrar lógicamente el servicio"""
@app.route('/usuarios/<int:id_user>/servicios/<int:id_servicio>', methods=['DELETE'])
@token_required
@user_resources
@servicio_resource
def remove_servicios(id_user, id_servicio):
    cur = mysql.connection.cursor()

    # Actualizar la columna activo en lugar de eliminar la fila
    cur.execute('UPDATE servicios SET activo = 0 WHERE id = {0}'.format(id_servicio))
    mysql.connection.commit()

    return jsonify({"message": "borrado lógico realizado", "id": id_servicio})


"""Consultar servicio por id"""
@app.route('/usuarios/<int:id_user>/servicios/<int:id_servicio>', methods=['GET'])
@token_required
@user_resources
@servicio_resource
def get_servicio_by_id(id_user, id_servicio):  # Agregar id_user e id_servicio como parámetros
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM servicios WHERE id = %s', (id_servicio,))
    data = cur.fetchall()

    if cur.rowcount > 0:
        objServ = Servicio(data[0])
        return jsonify(objServ.to_json())

    return jsonify({"message": "Servicio no encontrado"}), 404






@app.route('/usuarios/<int:id_user>/ranking-servicios', methods=['GET'])
@token_required
@user_resources
def get_ranking_servicios(id_user):
    try:
        cur = mysql.connection.cursor()

        # Consultar el ranking de servicios más vendidos para un usuario específico
        cur.execute('''
            SELECT S.nombre, SUM(DF.cantidad) as cantidad_vendida
            FROM detalle_factura DF
            JOIN servicios S ON DF.id_servicio = S.id
            JOIN factura F ON DF.id_factura = F.id
            WHERE F.id_usuario = %s
            GROUP BY DF.id_servicio
            ORDER BY cantidad_vendida DESC
            LIMIT 5
        ''', (id_user,))

        ranking_servicios = cur.fetchall()

        if not ranking_servicios:
            return jsonify({"message": "No hay servicios vendidos para este usuario"}), 404

        # Crear una lista de resultados
        resultados = []

        for servicio in ranking_servicios:
            nombre_servicio = servicio[0]
            cantidad_vendida = servicio[1]

            resultado = {
                "nombre_servicio": nombre_servicio,
                "cantidad_vendida": cantidad_vendida
            }

            resultados.append(resultado)

        return jsonify(resultados)

    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Endpoint para obtener el total de clientes
@app.route('/usuarios/<int:id_user>/servicios/total', methods=['GET'])
@token_required
@user_resources
def get_total_servicios(id_user):
    cur = mysql.connection.cursor()
    cur.execute('SELECT COUNT(*) FROM servicios WHERE id_usuario = {0} AND activo = 1'.format(id_user))
    total_servicios = cur.fetchone()[0]
    return jsonify({'total': total_servicios})




@app.route('/usuarios/<int:id_user>/servicios-paginados', methods=['GET'])
@token_required
@user_resources
def get_paginated_servicios(id_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 5  # Número de servicios por página

        cur = mysql.connection.cursor()
        cur.execute('SELECT COUNT(*) FROM servicios WHERE id_usuario = %s AND activo = 1', (id_user,))
        total_products = cur.fetchone()[0]

        cur.execute('SELECT * FROM servicios WHERE id_usuario = %s AND activo = 1 LIMIT %s OFFSET %s', (id_user, per_page, (page - 1) * per_page))
        print(cur.mogrify('SELECT * FROM servicios WHERE id_usuario = %s AND activo = 1 LIMIT %s OFFSET %s',
                          (id_user, per_page, (page - 1) * per_page)))
        data = cur.fetchall()

        serviceList = []

        for row in data:
            objServicios = Servicio(row)
            serviceList.append(objServicios.to_json())

        total_pages = ceil(total_products / per_page)
        current_page = page

        response_data = {
            "total_pages": total_pages,
            "current_page": current_page,
            "service": serviceList
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"message": str(e)}), 500
