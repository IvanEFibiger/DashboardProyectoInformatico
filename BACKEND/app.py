import datetime
from functools import wraps
from datetime import timedelta
import jwt
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_mysqldb import MySQL
from datetime import datetime
from datetime import date
from Users import *
from Clientes import *
from Productos import *
from Servicios import *
from detalle_factura import *
from factura import *
from math import ceil

# Crear una instancia de la aplicación Flask
app = Flask(__name__)
CORS(app)  # Habilitar el manejo de solicitudes CORS

# Configuración de la base de datos y la clave secreta
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'user_api_flask'
app.config['MYSQL_PASSWORD'] ='19Ivan88'
app.config['MYSQL_DB'] = 'db_proyecto_informatico'
app.config['SECRET_KEY'] = 'app_123'


mysql = MySQL(app)  # Crear una instancia de MySQL para interactuar con la base de datos

@app.route("/")
def index():
   return jsonify({"message": "API desarrollada con Flask"})

# Ruta para autenticar usuarios
@app.route("/login", methods=['POST'])
def login():
   auth = request.authorization

   # Control: Verificar que se proporcionen credenciales de autenticación
   if not auth or not auth.username or not auth.password:
       return jsonify({"message": 'No autorizado'}), 401

   # Control: Verificar las credenciales en la base de datos
   cur = mysql.connection.cursor()
   cur.execute('SELECT * FROM usuarios WHERE email = %s AND password = %s', (auth.username, auth.password))
   row = cur.fetchone()

   if not row:
       return jsonify({"message": 'No autorizado'}), 401

   # El usuario existe en la base de datos y se genera un token JWT
   token = jwt.encode({
       'id': row[0],
       'exp': datetime.utcnow() + timedelta(minutes=150)
   }, app.config['SECRET_KEY'])

   return jsonify({"token": token, 'username': auth.username, "id": row[0]})


@app.route("/logout", methods=['POST'])

def logout():
    auth_header = request.headers.get('Authorization')

    # Control: Verificar si se proporciona el encabezado de autorización
    if not auth_header:
        return jsonify({"error": 'No se proporcionó el encabezado de autorización'}), 401

    # Obtener el token del encabezado de autorización
    token = auth_header.split(" ")[1] if auth_header else None

    # Control: Verificar si se proporciona un token
    if not token:
        return jsonify({"error": 'No se proporcionó un token válido'}), 401

    # Enviar una respuesta exitosa
    return jsonify({"message": 'Sesión cerrada correctamente'}), 200





def token_required(func):
   @wraps(func)
   def decorated(*args, **kwargs):
       # Control: Verificar la existencia de un token en las cabeceras de la solicitud
       token = None
       if 'x-access-token' in request.headers:
           token = request.headers['x-access-token']
       if not token:
           return jsonify({
               "message": "Falta el Token"
           }), 401

       user_id = None
       if 'user-id' in request.headers:
           user_id = request.headers['user-id']
       if not user_id:
           return jsonify({"message": "falta usuario"}), 401

       try:
           data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
           token_id = data['id']

           # Control: Verificar si el ID del usuario coincide con el ID del token
           if int(user_id) != int(token_id):
               return jsonify({"message": "error de ID"}), 401
       except Exception as e:
           print(e)
           return jsonify({"message": str(e)}), 401
       return func(*args, **kwargs)
   return decorated



def user_resources(func):
   @wraps(func)
   def decorated(*args, **kwargs):
       id_user_route = kwargs['id_user']
       user_id = request.headers['user-id']

       # Control: Verificar si el ID del usuario en la ruta coincide con el ID del usuario autenticado
       if int(id_user_route) != int(user_id):
           return jsonify({"message": "no tiene permisos para acceder a este recurso de usuario"}), 401
       return func(*args, **kwargs)
   return decorated

def client_resource(func):
   @wraps(func)
   def decorated(*args, **kwargs):
       id_cliente = kwargs['id_client']
       print("Argumentos en client_resource:", kwargs)
       cur = mysql.connection.cursor()
       cur.execute('SELECT id_usuario FROM clientes WHERE id = {0}'.format(id_cliente))
       data = cur.fetchone()
       if data:
           """print(data)"""
           id_prop = data[0]
           user_id = request.headers['user-id']
           if int(id_prop) != int(user_id):
               return jsonify({'message': 'No tiene permisos para acceder a este recurso'}), 401
       return func(*args, **kwargs)
   return decorated

def  producto_resource(func):
   @wraps(func)
   def decorated(*args, **kwargs):
       print("Argumentos en producto_resource: ", kwargs)
       id_producto = kwargs['id_producto']
       cur = mysql.connection.cursor()
       cur.execute('SELECT id_usuario FROM productos WHERE id = {0}'.format(id_producto))
       data = cur.fetchone()
       if data:
           id_prop = data[0]
           user_id = request.headers['user_id']
           if int(user_id) != int(id_prop):
               return jsonify({'message': 'No tiene permisos para acceder a este recurso'}), 401
       return func(*args, **kwargs)
   return decorated

def  servicio_resource(func):
   @wraps(func)
   def decorated(*args, **kwargs):
       print("Argumentos en servicio_resource: ", kwargs)
       id_servicio = kwargs['id_servicio']
       cur = mysql.connection.cursor()
       cur.execute('SELECT id_usuario FROM servicios WHERE id = {0}'.format(id_servicio))
       data = cur.fetchone()
       if data:
           id_prop = data[0]
           user_id = request.headers['user_id']
           if int(user_id) != int(id_prop):
               return jsonify({'message': 'No tiene permisos para acceder a este recurso'}), 401
       return func(*args, **kwargs)
   return decorated

def factura_resource(func):
   @wraps(func)
   def decorated(*args, **kwargs):
       print("Argumentos en factura_resource: ", kwargs)
       id_factura = kwargs['id_factura']
       cur = mysql.connection.cursor()
       cur.execute('SELECT id_usuario FROM factura WHERE id = {0}'.format(id_factura))
       data = cur.fetchone()
       if data:
           id_prop = data[0]
           user_id = request.headers['user_id']
           if int(user_id) != int(id_prop):
               return jsonify({'message': 'No tiene permisos para acceder a este recurso'}), 401
       return func(*args, **kwargs)
   return decorated

def detalle_factura_resource(func):
   @wraps(func)
   def decorated(*args, **kwargs):
       print("Argumentos en detalle_factura_resource: ", kwargs)
       id_detalle_factura = kwargs['id_detalle_factura']
       cur = mysql.connection.cursor()
       cur.execute('SELECT id_usuario FROM detalle_factura WHERE id = {0}'.format(id_detalle_factura))
       data = cur.fetchone()
       if data:
           id_prop = data[0]
           user_id = request.headers['user_id']
           if int(user_id) != int(id_prop):
               return jsonify({'message': 'No tiene permisos para acceder a este recurso'}), 401
       return func(*args, **kwargs)
   return decorated

"""usuarios"""
# Definir la ruta para obtener los datos del usuario por ID
@app.route('/usuarios/<int:id_user>', methods=['GET'])
@token_required
@user_resources
def get_user_by_id(id_user):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE id = %s', (id_user,))
        data = cur.fetchall()

        if cur.rowcount > 0:
            objusuario = User(data[0])
            user_data = objusuario.to_dict()

            # Devuelve el nombre del usuario junto con los demás datos
            return jsonify({"user_data": user_data, "message": "Usuario obtenido exitosamente"}), 200

        return jsonify({"message": "ID de usuario no encontrado"}), 404

    except Exception as e:
        return jsonify({"message": str(e)}), 500





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


# Ejecutar la aplicación en modo de depuración en el puerto 4500
if __name__ == "__main__":
   app.run(debug=True, port=5500)

