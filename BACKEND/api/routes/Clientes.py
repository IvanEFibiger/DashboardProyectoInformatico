from api import app
from api.models.Clientes import Clientes
from api.Utilidades import *
from flask import request, jsonify
from api.db.db import mysql
from math import ceil

"""Clientes"""



"""Obtener todos los clientes"""
@app.route('/usuarios/<int:id_user>/clientes', methods=['GET'])
@token_required
@user_resources
def get_all_clientes(id_user):
   cur = mysql.connection.cursor()
   cur.execute('SELECT * FROM clientes WHERE id_usuario = %s AND activo = 1', (id_user,))
   data = cur.fetchall()
   personList = []

   for row in data:
       objCliente = Clientes(row)
       personList.append(objCliente.to_json())

   return jsonify(personList)

"""Crear un cliente"""

"""Crear un cliente"""
@app.route('/usuarios/<int:id_user>/clientes', methods=['POST'])
@token_required
@user_resources
def create_cliente(id_user):
   try:
       nombre = request.get_json()["nombre"]
       email = request.get_json()["email"]
       direccion = request.get_json()["direccion"]
       cuit = request.get_json()["cuit"]
       id_usuario = id_user

       cur = mysql.connection.cursor()

       # Buscar si ya existe un cliente con el mismo cuit (incluso si está inactivo)
       cur.execute("SELECT * FROM clientes WHERE cuit = %s", (cuit,))
       existing_client = cur.fetchone()

       print(existing_client)  # Imprime información de depuración

       if existing_client:
           # Obtener el índice del campo 'activo' en la descripción de la consulta
           activo_index = [desc[0] for desc in cur.description].index('activo')

           # Si el cliente existe y está inactivo, reactivarlo
           if existing_client[activo_index] == 0:
               cur.execute('UPDATE clientes SET activo = 1 WHERE id = %s', (existing_client[0],))
               mysql.connection.commit()
               return jsonify({"message": "Cliente reactivado", "id": existing_client[0]})

           # Si el cliente existe y está activo, devolver un mensaje indicando que ya está registrado
           return jsonify({"message": "Cliente ya registrado"})

       # Si no existe un cliente con el mismo cuit, crear uno nuevo
       cur.execute('INSERT INTO clientes (nombre, email, direccion, cuit, id_usuario) VALUES (%s, %s, %s, %s, %s)', (nombre, email, direccion, cuit, id_usuario))
       mysql.connection.commit()

       # Obtener el ID del registro creado
       cur.execute('SELECT LAST_INSERT_ID()')
       row = cur.fetchone()
       id = row[0]

       return jsonify({"nombre": nombre, "email": email, "direccion": direccion, "cuit": cuit, "id_usuario": id_usuario, "id": id})

   except Exception as e:
       return jsonify({"message": str(e)}), 500  # Devolver un mensaje de error y código 500 en caso de excepción


"""Actualizar el cliente"""
@app.route('/usuarios/<int:id_user>/clientes/<int:id_client>', methods=['PUT'])
@token_required
@user_resources
@client_resource
def update_cliente(id_user, id_client):
   nombre = request.get_json()["nombre"]
   email = request.get_json()["email"]
   direccion = request.get_json()["direccion"]
   cuit = request.get_json()["cuit"]

   cur = mysql.connection.cursor()
   cur.execute("UPDATE clientes SET nombre = %s, email = %s, direccion = %s, cuit = %s WHERE id = %s", (nombre, email, direccion, cuit, id_client))
   mysql.connection.commit()

   return jsonify({"id": id_client, "nombre": nombre, "email": email, "direccion": direccion, "cuit": cuit})

"""Eliminado logico de cliente"""
@app.route('/usuarios/<int:id_user>/clientes/<int:id_client>', methods=['DELETE'])
@token_required
@user_resources
@client_resource
def remove_clientes(id_user, id_client):
   cur = mysql.connection.cursor()
   cur.execute('UPDATE clientes SET activo = 0 WHERE id = {0}'.format(id_client))
   mysql.connection.commit()

   return jsonify({"message": "borrado lógico realizado", "id": id_client})


"""obtener cliente por id"""
@app.route('/usuarios/<int:id_user>/clientes/<int:id_client>', methods=['GET'])
@token_required
@user_resources
@client_resource
def get_cliente_by_id(id_user, id_client):
   cur = mysql.connection.cursor()
   cur.execute('SELECT * FROM clientes WHERE id = %s AND activo = 1', (id_client,))
   data = cur.fetchall()

   if cur.rowcount > 0:
       objcliente = Clientes(data[0])
       return jsonify(objcliente.to_json())

   return jsonify({"message": "ID no encontrado o cliente inactivo"})

"""Obtener la cantidad de clientes por cada usuario"""
@app.route('/usuarios/<int:id_user>/cantidad-clientes', methods=['GET'])
@token_required
@user_resources
def get_cantidad_clientes_por_usuario(id_user):
    try:
        cur = mysql.connection.cursor()

        # Consultar la cantidad de clientes para un usuario específico
        cur.execute('''
            SELECT COUNT(*) AS cantidad_clientes
            FROM clientes
            WHERE id_usuario = %s AND activo = 1
        ''', (id_user,))

        cantidad_clientes = cur.fetchone()

        if not cantidad_clientes:
            return jsonify({"message": "No hay clientes registrados para este usuario"}), 404

        # Crear un objeto de resultado
        result = {
            "id_usuario": id_user,
            "cantidad_clientes": cantidad_clientes[0]
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route('/usuarios/<int:id_user>/cliente-destacado', methods=['GET'])
@token_required
@user_resources
def get_cliente_destacado(id_user):
    try:
        cur = mysql.connection.cursor()

        # Consultar el cliente que más gastó para el usuario específico
        cur.execute('''
            SELECT C.nombre, SUM(F.total) as total_gastado
            FROM factura F
            JOIN clientes C ON F.id_clientes = C.id
            WHERE F.id_usuario = %s
            GROUP BY F.id_clientes
            ORDER BY total_gastado DESC
            LIMIT 1
        ''', (id_user,))

        cliente_destacado = cur.fetchone()

        if not cliente_destacado:
            return jsonify({"message": f"No hay facturas para el usuario con ID {id_user}"}), 404

        nombre_cliente = cliente_destacado[0]
        total_gastado = cliente_destacado[1]

        return jsonify({"cliente_destacado": nombre_cliente, "total_gastado": total_gastado})

    except Exception as e:
        return jsonify({"message": str(e)}), 500





@app.route('/usuarios/<int:id_user>/ranking-clientes', methods=['GET'])
@token_required
@user_resources
def get_ranking_clientes(id_user):
    try:
        cur = mysql.connection.cursor()

        # Consultar el ranking de los 5 clientes que más gastaron para el usuario específico
        cur.execute('''
            SELECT C.nombre, SUM(F.total) as total_gastado
            FROM factura F
            JOIN clientes C ON F.id_clientes = C.id
            WHERE F.id_usuario = %s
            GROUP BY F.id_clientes
            ORDER BY total_gastado DESC
        ''', (id_user,))

        ranking_clientes = cur.fetchall()

        if not ranking_clientes:
            return jsonify({"message": f"No hay facturas para el usuario con ID {id_user}"}), 404

        # Crear una lista de resultados
        resultados = []

        # Iterar sobre los resultados y agregarlos a la lista
        for cliente in ranking_clientes:
            nombre_cliente = cliente[0]
            total_gastado = cliente[1]

            resultado = {
                "nombre_cliente": nombre_cliente,
                "total_gastado": total_gastado
            }

            resultados.append(resultado)

        # Limitar a los primeros 5 resultados si hay más de 5 clientes
        resultados = resultados[:5]

        return jsonify(resultados)

    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Endpoint para obtener el total de clientes
@app.route('/usuarios/<int:id_user>/clientes/total', methods=['GET'])
@token_required
@user_resources
def get_total_clientes(id_user):
    cur = mysql.connection.cursor()
    cur.execute('SELECT COUNT(*) FROM clientes WHERE id_usuario = {0} AND activo = 1'.format(id_user))
    total_clientes = cur.fetchone()[0]
    return jsonify({'total': total_clientes})




@app.route('/usuarios/<int:id_user>/clientes-paginados', methods=['GET'])
@token_required
@user_resources
def get_paginated_clientes(id_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 5  # Número de clientes por página

        cur = mysql.connection.cursor()
        cur.execute('SELECT COUNT(*) FROM clientes WHERE id_usuario = %s AND activo = 1', (id_user,))
        total_clients = cur.fetchone()[0]

        cur.execute('SELECT * FROM clientes WHERE id_usuario = %s AND activo = 1 LIMIT %s OFFSET %s', (id_user, per_page, (page - 1) * per_page))
        print(cur.mogrify('SELECT * FROM clientes WHERE id_usuario = %s AND activo = 1 LIMIT %s OFFSET %s',
                          (id_user, per_page, (page - 1) * per_page)))
        data = cur.fetchall()

        personList = []

        for row in data:
            objCliente = Clientes(row)
            personList.append(objCliente.to_json())

        total_pages = ceil(total_clients / per_page)
        current_page = page

        response_data = {
            "total_pages": total_pages,
            "current_page": current_page,
            "clients": personList
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"message": str(e)}), 500

