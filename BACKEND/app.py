from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
import jwt
import datetime
from functools import wraps
from flask_cors import CORS

# Crear una instancia de la aplicación Flask
app = Flask(__name__)
CORS(app)  # Habilitar el manejo de solicitudes CORS

# Configuración de la base de datos y la clave secreta
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'user_api_flask'
app.config['MYSQL_PASSWORD'] ='19Ivan88'
app.config['MYSQL_DB'] = 'db_pryecto_informatico'
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
    cur.execute('SELECT * FROM usaurio WHERE user = %s AND password = %s', (auth.username, auth.password))
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



































# Ejecutar la aplicación en modo de depuración en el puerto 4500
if __name__ == "__main__":
    app.run(debug=True, port=4500)
