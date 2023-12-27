# **DASHBOARD PROYECTO INFORMATICO**

**Universidad Provincial del Sudoeste**
Tecnicatura Universitaria en Tecnologias de Programación
Materia: Proyecto Informatico
Profesor: Berger, Carlos
Grupo 7
Integrantes: Saavedra Daiana, Fibiger Ivan

# **ESTRUCTURA Y LANZAMIENTO DE APLICACIÓN:**
1. Crear Directorio de proyecto (PROYECTO INFORMATICO)
2. Crear subdirectorios (FRONTEND y BACKEND)
3. Cargar BACKEND en Pycharm
4. Creamos el archivo de requisitos
5. Instalar Dependencias
6. Crear estructura de directorios:
   BACKEND
        api
            models
                   Clientes.py
                   detalle_factura.py
                   factura.py
                   movimiento_stock.py
                   Productos.py
                   Servicios.py
                   Users.py
            routes
                   Clientes.py
                   factura.py
                   movimiento_stock.py
                   Productos.py
                   Servicios.py
                   Users.py
            db
            __init__.py
            Utilidades.py
        main.py
        requirements.txt
   FRONTEND
        Clientes.html
        dashboard.html
        Facturas.html 
        Productos.html
        Servicios.html
7. Ejecutar xampp y main.py
8. Cargar directorio FRONTEND en Visual Studio Code y ejecutar index.html

# **RUTAS:**
## **Rutas de Usuarios:**

@app.route("/login", methods=['POST'])
Autenticación de usuarios.

@app.route('/usuarios/<int:id_user>', methods=['GET'])
Obtener usuarios por id

@app.route("/logout", methods=['POST'])
Deslogueo

## **Rutas de clientes:**

@app.route('/usuarios/<int:id_user>/clientes', methods=['GET'])
Ruta para obtener todos los clientes de un usuario.

@app.route('/usuarios/<int:id_user>/clientes', methods=['POST'])
Ruta para agregar un cliente a un usuario.
Para ingresar un nuevo cliente:
{
  "nombre": "Cooperativa",
  "email": "coope@mail.com",
  "direccion": "calle 7 100",
  "cuit": 30504978552,
  "id_usuario": 1
}

@app.route('/usuarios/<int:id_user>/clientes/<int:id_client>', methods=['PUT'])
Ruta para actualizar un cliente:
{
  "nombre": "Cooperativa",
  "email": "coope@mail.com",
  "direccion": "calle 7 100",
  "cuit": 30504978552
}

@app.route('/usuarios/<int:id_user>/clientes/<int:id_client>', methods=['DELETE'])
Ruta para eliminar un cliente. (Borrado Logico).

@app.route('/usuarios/<int:id_user>/clientes/<int:id_client>', methods=['GET'])
Ruta para obtener el cliente por su id.

@app.route('/usuarios/<int:id_user>/cantidad-clientes', methods=['GET'])
Devuelve la cantidad de clientes registrados por usuario.

@app.route('/usuarios/<int:id_user>/cliente-destacado', methods=['GET'])
Devuelve el usuario que gasto mas dinero en sus compras.

@app.route('/usuarios/<int:id_user>/ranking-clientes', methods=['GET'])
Devuelve los clientes ordenados segun lo gastado.

@app.route('/usuarios/<int:id_user>/clientes/total', methods=['GET'])
Devuelve solo el numero de clientes registrados.

@app.route('/usuarios/<int:id_user>/clientes-paginados', methods=['GET'])
Devuelve los clientes registrados de a 5 por pagina.

## **Rutas de Productos:**
@app.route('/usuarios/<int:id_user>/productos', methods=['GET'])
Obtener todos los productos por usuarios

@app.route('/usuarios/<int:id_user>/productos/stock-positivo', methods=['GET'])
Devuelve solo aquellos productos con stock positivo.

@app.route('/usuarios/<int:id_user>/productos', methods=['POST'])
Ruta para crear nuevo producto.
Entrada:
{
  "nombre": "PC AIO ASUS v1",
  "descripcion": "i7 13900, 32gb Ram DDR5, SSD M.2 512gb",
  "precio": 250000,
  "cantidad":20,
  "id_usuario": 1
}

@app.route('/usuarios/<int:id_user>/productos/<int:id_producto>', methods=['PUT'])
Ruta para modificar producto por su id.
entrada:
{
  "nombre": "PC AIO SAMSUNG",
  "descripcion": "i7 12900, 16 RAM DDR4, SSD M.2 980GB",
  "precio": 600000,
  "cantidad": 10
}


@app.route('/usuarios/<int:id_user>/productos/<int:id_producto>/stock', methods=['PUT'])
Ruta para unicamente modificar la cantidad para el control stock.
entrada:
{
  "cantidad": 20
}

@app.route('/usuarios/<int:id_user>/productos/<int:id_producto>', methods=['DELETE'])
Ruta para eliminar un producto.


@app.route('/usuarios/<int:id_user>/productos/<int:id_producto>', methods=['GET'])
Ruta para obtener un producto por su id.

@app.route('/usuarios/<int:id_user>/ranking-productos', methods=['GET'])
Devuelve los productos mas vendidos de mayor a menor.

@app.route('/usuarios/<int:id_user>/productos/total', methods=['GET'])
Devuelve el total de productos.

@app.route('/usuarios/<int:id_user>/productos-paginados', methods=['GET'])
Devuelve los productos de a 5 por pagina.

## **Rutas de Servicios:**

@app.route('/usuarios/<int:id_user>/servicios', methods=['GET'])
Ruta para obtener todos los servicios.

@app.route('/usuarios/<int:id_user>/servicios', methods=['POST'])
Ruta para crear un nuevo servicio
Entrada:
{
  "nombre": "Formateo v4",
  "descripcion": "borrado y reinstalación de Sistema operativo y programas basicos",
  "precio": 5500,
  "id_usuario": 1
}


@app.route('/usuarios/<int:id_user>/servicios/<int:id_servicio>', methods=['PUT'])
ruta para modificar un servicio:
{
  "nombre": "Formateo v34",
  "descripcion": "borrado y reinstalación de Sistema operativo y programas basicos",
  "precio": 9000
}


@app.route('/usuarios/<int:id_user>/servicios/<int:id_servicio>', methods=['DELETE'])
Ruta para borrado lógico de servicio.


@app.route('/usuarios/<int:id_user>/servicios/<int:id_servicio>', methods=['GET'])
Obtener servicio por id.

@app.route('/usuarios/<int:id_user>/ranking-servicios', methods=['GET'])
Devuelve los servicios ordenados por ventas de mayor a menor.

@app.route('/usuarios/<int:id_user>/servicios/total', methods=['GET'])
Devuelve el total de servicios cargados

@app.route('/usuarios/<int:id_user>/servicios-paginados', methods=['GET'])
devuelve los servicios de a 5 por pagina.

## **Rutas para Facturas:**


@app.route('/usuarios/<int:id_user>/factura', methods=['GET'])
Ruta para obtener todas las facturas de un usuario.

@app.route('/usuarios/<int:id_user>/factura', methods=['POST'])
Ruta para crear una nueva factura.
Entrada para un solo producto o servicio:
{
    "fecha_emision": "2023-11-21",
    "id_clientes": 4,
    "id_usuario": 1,
    "productos_servicios": [
        {
            "cantidad": 5,
            "id_producto": 21,
            "id_servicio": null
        }
            ]
}

Para dos o mas:

{
    "fecha_emision": "2023-11-21",
    "id_clientes": 4,
    "id_usuario": 1,
    "productos_servicios": [
        {
            "cantidad": 5,
            "id_producto": 21,
            "id_servicio": null
        },
        {
            "cantidad": 5,
            "id_producto": 23,
            "id_servicio": null
        },
        {
            "cantidad": 1,
            "id_producto": null,
            "id_servicio": 8
        }
    ]
}

"""Actualizar factura por id"""
@app.route('/usuarios/<int:id_user>/factura/<int:id_factura>', methods=['PUT'])
actualizar factura por id. Solo se permite la modificación de cliente y fecha.
Entrada:
{
  "fecha_emision": "2023-08-21",
  "id_clientes": 1
}


@app.route('/usuarios/<int:id_user>/factura/<int:id_factura>', methods=['DELETE'])
Borrado lógico de factura.


@app.route('/usuarios/<int:id_user>/factura/<int:id_factura>', methods=['GET'])
Consultar factura por id. En este caso se muestra la factura con todos sus detalles.

@app.route('/usuarios/<int:id_user>/factura/total', methods=['GET'])
Devuelve el valor total de facturas generadas por el usuario

@app.route('/usuarios/<int:id_user>/factura/cantidad', methods=['GET'])
Devuelve la cantidad de facturas generadas por el usuario.

@app.route('/usuarios/<int:id_user>/factura/producto-mas-vendido', methods=['GET'])
Devuelve el producto mas presente en todas las facturas.

@app.route('/usuarios/<int:id_user>/factura/servicio-mas-vendido', methods=['GET'])
Devuelve el servicio mas presente en todas las facturas.

@app.route('/usuarios/<int:id_user>/facturas/detalles', methods=['GET'])
Devuelve las facturas de a 5 por pagina.

## **Rutas Movimientos de Stock:**


@app.route('/usuarios/<int:id_user>/stock_movimientos', methods=['GET'])
Ruta para obtener todos los movimientos de stock de un usuario.

@app.route('/usuarios/<int:id_user>/productos/<int:id_producto>/ultimo_stock', methods=['GET'])
Obtiene el ultimo movimiento de stock registrado.

@app.route('/usuarios/<int:id_user>/stock_movimientos/<int:id_producto>', methods=['GET'])
Obtiene el historial de movimientos para cada producto.

@app.route('/usuarios/<int:id_user>/historial_ventas', methods=['GET'])
Obtiene el historial de ventas.







