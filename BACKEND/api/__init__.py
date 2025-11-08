# api/__init__.py
import os
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from dotenv import load_dotenv
from api.db.db import mysql

from api.utils.extensions import limiter

load_dotenv()

app = Flask(__name__)


FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
CORS(
    app,
    resources={r"/*": {"origins": [FRONTEND_ORIGIN]}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)


app.config['SECRET_KEY']        = os.getenv('SECRET_KEY', 'dev-secret')
app.config['MYSQL_HOST']        = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_PORT']        = int(os.getenv('MYSQL_PORT', '3306'))
app.config['MYSQL_USER']        = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD']    = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB']          = os.getenv('MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = os.getenv('MYSQL_CURSORCLASS', 'DictCursor')
app.config['MYSQL_CHARSET']     = os.getenv('MYSQL_CHARSET', 'utf8mb4')

app.config['JWT_ISS']           = os.getenv('JWT_ISS', 'id-smart-solutions')
app.config['JWT_AUD']           = os.getenv('JWT_AUD', 'dashboard-api')
app.config['ACCESS_TTL_MIN']    = int(os.getenv('ACCESS_TTL_MIN', '30'))
app.config['REFRESH_TTL_DAYS']  = int(os.getenv('REFRESH_TTL_DAYS', '15'))

mysql.init_app(app)


app.config['RATELIMIT_DEFAULT']      = ["200 per day", "50 per hour"]
app.config['RATELIMIT_STORAGE_URI']  = os.getenv("FLASK_LIMITER_STORAGE_URI", "memory://")

limiter.init_app(app)


@limiter.request_filter
def _skip_preflight():
    return request.method == "OPTIONS"


@app.route('/<path:_path>', methods=['OPTIONS'])
def any_options(_path):
   
    return make_response(('', 204))


from api.routes.auth import auth_bp             
from api.routes.AuthRefresh import refresh_bp   

app.register_blueprint(auth_bp, url_prefix="")
app.register_blueprint(refresh_bp)

import api.routes.Users               
import api.routes.factura             
import api.routes.Servicios           
import api.routes.Productos           
import api.routes.Clientes            
import api.routes.movimiento_stock    

@app.get("/health")
def health():
    return jsonify({"status": "ok"})
