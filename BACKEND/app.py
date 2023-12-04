import datetime
from functools import wraps
from datetime import timedelta
import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL
from datetime import datetime
from datetime import date
from Clientes import *
from Productos import *
from Servicios import *
from detalle_factura import *
from factura import *

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

"""Clientes"""

"""Obtener todos los clientes"""
@app.route('/usuarios/<int:id_user>/clientes', methods=['GET'])
@token_required
@user_resources
def get_all_clientes(id_user):
   cur = mysql.connection.cursor()
   cur.execute('SELECT * FROM clientes WHERE id_usuario = {0} AND activo = 1'.format(id_user))
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


"""Crear factura"""
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

               # Verificar que la cantidad de cada producto sea mayor que cero
               for producto_servicio in productos_servicios:
                   cantidad = producto_servicio["cantidad"]
                   if cantidad <= 0:
                       return jsonify({"message": "La cantidad de cada producto debe ser mayor que cero"}), 400

               # Obtener la fecha de la factura
               fecha_factura = fecha_emision

               cur = mysql.connection.cursor()

               # Obtener el último valor de stock_real para ese producto
               cur.execute(
                   'SELECT stock_real FROM movimiento_stock WHERE producto_id = %s ORDER BY fecha DESC LIMIT 1',
                   (id_producto,))
               ultimo_stock_real = cur.fetchone()

               # Obtener la cantidad de la factura
               cantidad_factura = producto_servicio["cantidad"]

               if "id_producto" in producto_servicio and producto_servicio["id_producto"]:
                   id_producto = producto_servicio["id_producto"]

                   # Obtener el último valor de stock_real para ese producto
                   cur.execute(
                       'SELECT stock_real FROM movimiento_stock WHERE producto_id = %s ORDER BY fecha DESC LIMIT 1',
                       (id_producto,))
                   ultimo_stock_real = cur.fetchone()

                   # Obtener el último stock_real o establecerlo en 0 si no hay registros
                   stock_anterior = ultimo_stock_real[0] if ultimo_stock_real else 0

                   # Verificar si hay suficiente stock disponible
                   if stock_anterior < cantidad_factura:
                       # Si no hay suficiente stock, devolver un mensaje de error
                       return jsonify({
                           "message": f"No hay suficiente stock disponible para el producto con ID {id_producto}"}), 500

                   # Calcular el nuevo stock_real
                   nuevo_stock_real = stock_anterior - cantidad_factura if isinstance(stock_anterior, int) else 0

                   # Restar la cantidad en la columna stock_real en movimiento_stock
                   cur.execute(
                       'INSERT INTO movimiento_stock (producto_id, tipo, cantidad, fecha, stock_real) VALUES (%s, %s, %s, %s, %s)',
                       (id_producto, 'salida', cantidad_factura, fecha_factura, nuevo_stock_real))
                   mysql.connection.commit()

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
               else:
                   return jsonify(
                       {"message": f"No se encontró el precio para el {'producto' if id_producto else 'servicio'} con ID {id_producto or id_servicio}"}), 500

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
def consultar_factura(id_user, id_factura):  # Agregar id_user e id_factura como parámetros
    cur = mysql.connection.cursor()

    # Consultar factura por ID
    cur.execute('SELECT * FROM Factura WHERE id = %s', (id_factura,))
    data_factura = cur.fetchall()

    if cur.rowcount == 0:
        return jsonify({"message": "Factura no encontrada"}), 404

    obj_factura = Factura(data_factura[0])
    factura_info = obj_factura.to_json()

    # Calcular el total de la factura
    cur.execute('SELECT total FROM Factura WHERE id = %s', (id_factura,))
    total_row = cur.fetchone()
    total = total_row[0] if total_row and total_row[0] is not None else 0

    # Consultar detalle de factura por ID de factura
    cur.execute('SELECT * FROM Detalle_factura WHERE id_factura = %s', (id_factura,))
    data_detalle = cur.fetchall()

    detalle_list = []
    for row in data_detalle:
        obj_detalle = DetalleFactura(row)
        detalle_list.append(obj_detalle.to_json())

    # Consultar productos y servicios asociados al detalle de factura
    productos_servicios_list = []
    for detalle in detalle_list:
        if detalle["id_producto"]:
            cur.execute('SELECT * FROM Productos WHERE id = %s', (detalle["id_producto"],))
            data_producto = cur.fetchone()
            obj_producto = Producto(data_producto)
            productos_servicios_list.append(obj_producto.to_json())
        elif detalle["id_servicio"]:
            cur.execute('SELECT * FROM Servicios WHERE id = %s', (detalle["id_servicio"],))
            data_servicio = cur.fetchone()
            obj_servicio = Servicio(data_servicio)
            productos_servicios_list.append(obj_servicio.to_json())

    # Organizar la salida
    output = {
        "factura": factura_info,
        "detalles": detalle_list,
        "productos_servicios": productos_servicios_list,
        "total": total
    }

    return jsonify(output)



"""Obtener los movimientos de stock"""
@app.route('/usuarios/<int:id_user>/stock_movimientos', methods=['GET'])
@token_required
@user_resources
def get_stock_movimientos(id_user):
   try:
       cur = mysql.connection.cursor()
       cur.execute('SELECT id, producto_id, tipo, cantidad, fecha, stock_real FROM movimiento_stock')

       data = cur.fetchall()
       stock_movimientos = []

       for row in data:
           movimiento_info = {
               "id": row[0],
               "producto_id": row[1],
               "tipo": row[2],
               "cantidad": row[3],
               "fecha": row[4],
               "stock_real": int(row[5])
           }

           # Actualizamos la información de stock para cada producto en cada iteración
           stock_movimientos.append(movimiento_info)

       return jsonify(stock_movimientos)

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





# Ejecutar la aplicación en modo de depuración en el puerto 4500
if __name__ == "__main__":
   app.run(debug=True, port=5500)

