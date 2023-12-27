from functools import wraps
from api import app
import jwt
from flask import request, jsonify
from api.db.db import mysql


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