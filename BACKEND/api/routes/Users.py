from api.models.Users import User
from api.Utilidades import *
from flask import request, jsonify
import jwt
import datetime
from datetime import datetime
from datetime import timedelta

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
