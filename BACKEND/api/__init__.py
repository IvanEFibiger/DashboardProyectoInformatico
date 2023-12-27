from flask import Flask, jsonify, request
from functools import wraps
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'app_123'

import api.routes.Users
import api.routes.factura
import api.routes.Servicios
import api.routes.Productos
import api.routes.Clientes
import api.routes.movimiento_stock
