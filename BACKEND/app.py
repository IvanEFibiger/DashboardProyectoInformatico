from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
import jwt
import datetime
from functools import wraps
from flask_cors import CORS
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
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=150)
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



"""Clientes"""

"""Obtener todos los clientes"""
@app.route('/clientes', methods=['GET'])
def get_all_clientes():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM clientes WHERE activo = 1')
    data = cur.fetchall()
    personList = []

    for row in data:
        objCliente = Clientes(row)
        personList.append(objCliente.to_json())

    return jsonify(personList)

"""Crear un cliente"""

"""Crear un cliente"""
@app.route('/clientes', methods=['POST'])
def create_cliente():
    try:
        nombre = request.get_json()["nombre"]
        email = request.get_json()["email"]
        direccion = request.get_json()["direccion"]
        cuit = request.get_json()["cuit"]
        id_usuario = request.get_json()["id_usuario"]

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
@app.route('/clientes/<int:id>', methods=['PUT'])
def update_cliente(id):
    nombre = request.get_json()["nombre"]
    email = request.get_json()["email"]
    direccion = request.get_json()["direccion"]
    cuit = request.get_json()["cuit"]
    #id_usuario = request.get_json()["id_usuario"]

    cur = mysql.connection.cursor()
    cur.execute("UPDATE clientes SET nombre = %s, email = %s, direccion = %s, cuit = %s WHERE id = %s", (nombre, email, direccion, cuit, id))
    mysql.connection.commit()

    return jsonify({"id": id, "nombre": nombre, "email": email, "direccion": direccion, "cuit": cuit})

"""Eliminado logico de cliente"""
@app.route('/clientes/<int:id>', methods=['DELETE'])
def remove_clientes(id):
    cur = mysql.connection.cursor()
    cur.execute('UPDATE clientes SET activo = 0 WHERE id = {0}'.format(id))
    mysql.connection.commit()

    return jsonify({"message": "borrado lógico realizado", "id": id})

"""obtener cliente por id"""

@app.route('/clientes/<int:id>', methods=['GET'])
def get_cliente_by_id(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM clientes WHERE id = %s AND activo = 1', (id,))
    data = cur.fetchall()

    if cur.rowcount > 0:
        objcliente = Clientes(data[0])
        return jsonify(objcliente.to_json())

    return jsonify({"message": "ID no encontrado o cliente inactivo"})



"""Productos"""

"""Obtener todos los productos"""
@app.route('/productos', methods=['GET'])
def get_all_productos():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM productos')
    data = cur.fetchall()
    prodList = []

    for row in data:
        objProd = Producto(row)
        prodList.append(objProd.to_json())

    return jsonify(prodList)


"""Crear nuevo producto"""

@app.route('/productos', methods=['POST'])
def create_producto():
    try:
        nombre = request.get_json()["nombre"]
        descripcion = request.get_json()["descripcion"]
        precio = request.get_json()["precio"]
        cantidad = request.get_json()["cantidad"]
        id_usuario = request.get_json()["id_usuario"]

        cur = mysql.connection.cursor()

        # Control: Verificar si el email ya está registrado
        cur.execute("SELECT * FROM productos WHERE nombre = %s", (nombre,))
        row = cur.fetchone()

        if row:
            return jsonify({"message": "producto ya registrado"})

        cur.execute('INSERT INTO productos (nombre, descripcion, precio, cantidad, id_usuario) VALUES (%s, %s, %s, %s, %s)', (nombre, descripcion, precio, cantidad, id_usuario))
        mysql.connection.commit()

        # Obtener el ID del registro creado
        cur.execute('SELECT LAST_INSERT_ID()')
        row = cur.fetchone()
        id = row[0]

        return jsonify({"nombre": nombre, "descripcion": descripcion, "precio": precio, "cantidad": cantidad, "id_usuario": id_usuario,"id": id})
    except Exception as e:
        return jsonify({"message": str(e)}), 500  # Devolver un mensaje de error y código 500 en caso de excepción

"""Modificar producto"""
@app.route('/productos/<int:id>', methods=['PUT'])
def update_producto(id):
    nombre = request.get_json()["nombre"]
    descripcion = request.get_json()["descripcion"]
    precio = request.get_json()["precio"]
    cantidad = request.get_json()["cantidad"]


    cur = mysql.connection.cursor()
    cur.execute("UPDATE productos SET nombre = %s, descripcion = %s, precio = %s, cantidad = %s WHERE id = %s", (nombre, descripcion, precio, cantidad, id))
    mysql.connection.commit()

    return jsonify({"id": id, "nombre": nombre, "descripcion": descripcion, "precio": precio, "cantidad": cantidad})

"""ELIMINAR Producto"""

@app.route('/productos/<int:id>', methods=['DELETE'])
def remove_producto(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM productos WHERE id = {0}'.format(id))
    mysql.connection.commit()

    return jsonify({"message": "eliminado", "id": id})


"""Consultar producto por id"""

@app.route('/productos/<int:id>', methods=['GET'])
def get_producto_by_id(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM productos WHERE id = %s', (id,))
    data = cur.fetchall()

    if cur.rowcount > 0:
        objcliente = Clientes(data[0])
        return jsonify(objcliente.to_json())

    return jsonify({"message": "ID no encontrado o producto sin stock"})



"""Servicios"""

"""Obtener todos los servicios"""
@app.route('/servicios', methods=['GET'])
def get_all_servicios():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM servicios')
    data = cur.fetchall()
    servList = []

    for row in data:
        objServ = Servicio(row)
        servList.append(objServ.to_json())

    return jsonify(servList)


"""Crear nuevo servicio"""

@app.route('/servicios', methods=['POST'])
def create_servicio():
    try:
        nombre = request.get_json()["nombre"]
        descripcion = request.get_json()["descripcion"]
        precio = request.get_json()["precio"]
        id_usuario = request.get_json()["id_usuario"]

        cur = mysql.connection.cursor()

        # Control: Verificar si el email ya está registrado
        cur.execute("SELECT * FROM servicios WHERE nombre = %s", (nombre,))
        row = cur.fetchone()

        if row:
            return jsonify({"message": "servicio ya registrado"})

        cur.execute('INSERT INTO servicios (nombre, descripcion, precio, id_usuario) VALUES (%s, %s, %s, %s)', (nombre, descripcion, precio, id_usuario))
        mysql.connection.commit()

        # Obtener el ID del registro creado
        cur.execute('SELECT LAST_INSERT_ID()')
        row = cur.fetchone()
        id = row[0]

        return jsonify({"nombre": nombre, "descripcion": descripcion, "precio": precio, "id_usuario": id_usuario,"id": id})
    except Exception as e:
        return jsonify({"message": str(e)}), 500  # Devolver un mensaje de error y código 500 en caso de excepción

"""Modificar servicio"""
@app.route('/servicios/<int:id>', methods=['PUT'])
def update_servicio(id):
    nombre = request.get_json()["nombre"]
    descripcion = request.get_json()["descripcion"]
    precio = request.get_json()["precio"]


    cur = mysql.connection.cursor()
    cur.execute("UPDATE servicios SET nombre = %s, descripcion = %s, precio = %s", (nombre, descripcion, precio))
    mysql.connection.commit()

    return jsonify({"id": id, "nombre": nombre, "descripcion": descripcion, "precio": precio})

"""ELIMINAR Servicio"""

@app.route('/servicios/<int:id>', methods=['DELETE'])
def remove_servicios(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM servicios WHERE id = {0}'.format(id))
    mysql.connection.commit()

    return jsonify({"message": "eliminado", "id": id})


"""Consultar servicio por id"""

@app.route('/servicios/<int:id>', methods=['GET'])
def get_servicio_by_id(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM servicios WHERE id = %s', (id,))
    data = cur.fetchall()

    if cur.rowcount > 0:
        objServ = Servicio(data[0])
        return jsonify(objServ.to_json())

    return jsonify({"message": "Servicio no encontrado"})


"""Detalle Factura"""

@app.route('/detalle_factura', methods=['GET'])
def get_all_detalle_factura():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Detalle_factura')
    data = cur.fetchall()
    detalleList = []

    for row in data:
        objDetalle = DetalleFactura(row)
        detalleList.append(objDetalle.to_json())

    return jsonify(detalleList)

@app.route('/detalle_factura', methods=['POST'])
def create_detalle_factura():
    try:
        id_factura = request.get_json()["id_factura"]
        id_producto = request.get_json()["id_producto"]
        id_servicio = request.get_json()["id_servicio"]
        cantidad = request.get_json()["cantidad"]
        precio_unitario = request.get_json()["precio_unitario"]
        subtotal = request.get_json()["subtotal"]

        cur = mysql.connection.cursor()

        cur.execute('INSERT INTO Detalle_factura (id_factura, id_producto, id_servicio, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s, %s)',
                    (id_factura, id_producto, id_servicio, cantidad, precio_unitario, subtotal))
        mysql.connection.commit()

        cur.execute('SELECT LAST_INSERT_ID()')
        row = cur.fetchone()
        detalle_id = row[0]

        return jsonify({"id_factura": id_factura, "id_producto": id_producto, "id_servicio": id_servicio, "cantidad": cantidad, "precio_unitario": precio_unitario, "subtotal": subtotal, "detalle_id": detalle_id})

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/detalle_factura/<int:detalle_id>', methods=['PUT'])
def update_detalle_factura(detalle_id):
    id_factura = request.get_json()["id_factura"]
    id_producto = request.get_json()["id_producto"]
    id_servicio = request.get_json()["id_servicio"]
    cantidad = request.get_json()["cantidad"]
    precio_unitario = request.get_json()["precio_unitario"]
    subtotal = request.get_json()["subtotal"]

    cur = mysql.connection.cursor()
    cur.execute("UPDATE Detalle_factura SET id_factura = %s, id_producto = %s, id_servicio = %s, cantidad = %s, precio_unitario = %s, subtotal = %s WHERE id = %s",
                (id_factura, id_producto, id_servicio, cantidad, precio_unitario, subtotal, detalle_id))
    mysql.connection.commit()

    return jsonify({"detalle_id": detalle_id, "id_factura": id_factura, "id_producto": id_producto, "id_servicio": id_servicio, "cantidad": cantidad, "precio_unitario": precio_unitario, "subtotal": subtotal})

@app.route('/detalle_factura/<int:detalle_id>', methods=['DELETE'])
def remove_detalle_factura(detalle_id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM Detalle_factura WHERE id = {0}'.format(detalle_id))
    mysql.connection.commit()

    return jsonify({"message": "eliminado", "detalle_id": detalle_id})

@app.route('/detalle_factura/<int:detalle_id>', methods=['GET'])
def get_detalle_factura_by_id(detalle_id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Detalle_factura WHERE id = %s', (detalle_id,))
    data = cur.fetchall()

    if cur.rowcount > 0:
        objDetalle = DetalleFactura(data[0])
        return jsonify(objDetalle.to_json())

    return jsonify({"message": "Detalle de factura no encontrado"})



"""factura"""

@app.route('/facturas', methods=['GET'])
def get_all_facturas():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM factura')
    data = cur.fetchall()
    facturaList = []

    for row in data:
        objFactura = Factura(row)
        facturaList.append(objFactura.to_json())

    return jsonify(facturaList)

@app.route('/facturas', methods=['POST'])

def create_factura():
    try:
        fecha_emision = request.get_json()["fecha_emision"]
        id_clientes = request.get_json()["id_clientes"]
        id_usuario = request.get_json()["id_usuario"]
        productos = request.get_json()["productos"]
        servicios = request.get_json()["servicios"]

        cur = mysql.connection.cursor()

        # Guarda la factura
        cur.execute('INSERT INTO Factura (fecha_emision, id_clientes, id_usuario) VALUES (%s, %s, %s)',
                    (fecha_emision, id_clientes, id_usuario))
        mysql.connection.commit()

        # Obtiene el ID de la factura recién creada
        cur.execute('SELECT LAST_INSERT_ID()')
        row = cur.fetchone()
        factura_id = row[0]

        # Guarda los detalles de la factura
        for producto_id in productos:
            cur.execute('INSERT INTO Detalle_factura (id_factura, id_producto, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)',
                        (factura_id, producto_id, 1, 0, 0))  # Ajusta los valores según tu lógica
            mysql.connection.commit()

        for servicio_id in servicios:
            cur.execute('INSERT INTO Detalle_factura (id_factura, id_servicio, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)',
                        (factura_id, servicio_id, 1, 0, 0))  # Ajusta los valores según tu lógica
            mysql.connection.commit()

        return jsonify({"factura_id": factura_id})

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route('/facturas/<int:factura_id>', methods=['PUT'])
def update_factura(factura_id):
    fecha_emision = request.get_json()["fecha_emision"]
    id_clientes = request.get_json()["id_clientes"]
    id_usuario = request.get_json()["id_usuario"]

    cur = mysql.connection.cursor()
    cur.execute("UPDATE factura SET fecha_emision = %s, id_clientes = %s, id_usuario = %s WHERE id = %s",
                (fecha_emision, id_clientes, id_usuario, factura_id))
    mysql.connection.commit()

    return jsonify({"factura_id": factura_id, "fecha_emision": fecha_emision, "id_clientes": id_clientes, "id_usuario": id_usuario})

@app.route('/facturas/<int:factura_id>', methods=['DELETE'])
def remove_factura(factura_id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM factura WHERE id = {0}'.format(factura_id))
    mysql.connection.commit()

    return jsonify({"message": "eliminada", "factura_id": factura_id})

@app.route('/facturas/<int:factura_id>', methods=['GET'])
def get_factura_by_id(factura_id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM factura WHERE id = %s', (factura_id,))
    data = cur.fetchall()

    if cur.rowcount > 0:
        objFactura = Factura(data[0])
        return jsonify(objFactura.to_json())

    return jsonify({"message": "Factura no encontrada"})









# Ejecutar la aplicación en modo de depuración en el puerto 4500
if __name__ == "__main__":
    app.run(debug=True, port=5500)
