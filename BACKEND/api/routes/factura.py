# api/routes/factura.py
from api import app
from api.models.factura import Factura
from api.models.Productos import Producto
from api.models.Servicios import Servicio
from api.models.detalle_factura import DetalleFactura
from api.Utilidades import token_required, user_resource_param, factura_resource
from flask import request, jsonify
from api.db.db import mysql
from math import ceil
from datetime import datetime
import MySQLdb.cursors as cursors
from api.utils.date_range import parse_from_to



@app.route('/usuarios/<int:id_user>/factura', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_all_facturas(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute('SELECT * FROM factura WHERE id_usuario = %s', (id_user,))
        data = cur.fetchall()
        factura_list = [Factura(row).to_json() for row in data]
        return jsonify(factura_list), 200
    finally:
        cur.close()



@app.route('/usuarios/<int:id_user>/factura', methods=['POST'])
@token_required
@user_resource_param("id_user")
def create_factura(id_user):
    try:
        body = request.get_json(force=True) or {}
        fecha_emision = (body.get("fecha_emision") or "").strip()
        id_clientes = body.get("id_clientes")
        productos_servicios = body.get("productos_servicios", [])

        if not fecha_emision or not id_clientes or not productos_servicios:
            return jsonify({"message": "fecha_emision, id_clientes y productos_servicios son obligatorios"}), 400


        try:
            if len(fecha_emision) == 10:
                _dt = datetime.strptime(fecha_emision, "%Y-%m-%d")
            else:
                _dt = datetime.fromisoformat(fecha_emision)
            fecha_emision_sql = _dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return jsonify({"message": "fecha_emision inválida"}), 400

        cur = mysql.connection.cursor(cursors.DictCursor)
        try:

            cur.execute(
                'SELECT id FROM clientes WHERE id = %s AND id_usuario = %s AND activo = 1',
                (id_clientes, id_user)
            )
            if not cur.fetchone():
                return jsonify({"message": "Cliente inexistente, inactivo o no pertenece al usuario"}), 403


            norm_items = [] 
            qty_by_product = {}  

            for idx, ps in enumerate(productos_servicios, start=1):
                cantidad = ps.get("cantidad")
                id_producto = ps.get("id_producto")
                id_servicio = ps.get("id_servicio")

                if cantidad is None or (not id_producto and not id_servicio):
                    return jsonify({"message": f"Item {idx}: requiere cantidad y (id_producto o id_servicio)"}), 400
                try:
                    cantidad = float(cantidad)
                    if cantidad <= 0:
                        return jsonify({"message": f"Item {idx}: cantidad debe ser > 0"}), 400
                except (ValueError, TypeError):
                    return jsonify({"message": f"Item {idx}: cantidad inválida"}), 400

                if id_producto:
                    pid = int(id_producto)
                    qty_by_product[pid] = qty_by_product.get(pid, 0.0) + cantidad
                    norm_items.append({"tipo": "producto", "id_producto": pid, "cantidad": cantidad})
                else:
                    sid = int(id_servicio)
                    norm_items.append({"tipo": "servicio", "id_servicio": sid, "cantidad": cantidad})


            product_info = {}   
            service_price = {}  

 
            for pid, cant_total in qty_by_product.items():
  
                cur.execute(
                    'SELECT id, precio FROM productos WHERE id = %s AND id_usuario = %s AND activo = 1',
                    (pid, id_user)
                )
                p = cur.fetchone()
                if not p:
                    mysql.connection.rollback()
                    return jsonify({"message": f"Producto {pid} inválido, inactivo o de otro usuario"}), 403

   
                cur.execute('''
                    SELECT stock_real
                    FROM movimiento_stock
                    WHERE producto_id = %s
                    ORDER BY id DESC
                    LIMIT 1
                    FOR UPDATE
                ''', (pid,))
                last = cur.fetchone()
                if not last or last["stock_real"] is None:
                    mysql.connection.rollback()
                    return jsonify({"message": f"No hay stock registrado para producto {pid}"}), 400

                disponible = float(last["stock_real"])
                if disponible < cant_total:
                    mysql.connection.rollback()
                    return jsonify({
                        "message": f"Stock insuficiente para producto {pid}",
                        "producto_id": pid,
                        "disponible": disponible,
                        "solicitado": cant_total,
                        "faltante": round(cant_total - disponible, 2)
                    }), 409

                product_info[pid] = {
                    "precio": float(p["precio"]),
                    "disponible": disponible
                }

            for it in norm_items:
                if it["tipo"] == "servicio":
                    sid = it["id_servicio"]
                    if sid in service_price:
                        continue
                    cur.execute(
                        'SELECT id, precio FROM servicios WHERE id = %s AND id_usuario = %s AND activo = 1',
                        (sid, id_user)
                    )
                    s = cur.fetchone()
                    if not s:
                        mysql.connection.rollback()
                        return jsonify({"message": f"Servicio {sid} inválido, inactivo o de otro usuario"}), 403
                    service_price[sid] = float(s["precio"])

      
            cur.execute(
                'INSERT INTO factura (fecha_emision, id_clientes, id_usuario, total) VALUES (%s, %s, %s, 0)',
                (fecha_emision_sql, id_clientes, id_user)
            )
            mysql.connection.commit()  
            factura_id = cur.lastrowid
            if not factura_id:
                mysql.connection.rollback()
                return jsonify({"message": "Error al obtener ID de factura"}), 500

            total = 0.0

            
            running_stock = {pid: info["disponible"] for pid, info in product_info.items()}

        
            for it in norm_items:
                cantidad = it["cantidad"]
                if it["tipo"] == "producto":
                    pid = it["id_producto"]
                    precio = product_info[pid]["precio"]
                    running_stock[pid] = float(running_stock[pid]) - float(cantidad)

             
                    subtotal = round(precio * cantidad, 2)
                    total += subtotal
                    cur.execute(
                        'INSERT INTO detalle_factura (id_factura, id_producto, id_servicio, cantidad, precio_unitario, subtotal) '
                        'VALUES (%s, %s, %s, %s, %s, %s)',
                        (factura_id, pid, None, cantidad, precio, subtotal)
                    )

                 
                    cur.execute(
                        'INSERT INTO movimiento_stock (producto_id, tipo, cantidad, fecha, stock_real) '
                        'VALUES (%s, %s, %s, %s, %s)',
                        (pid, 'salida', cantidad, fecha_emision_sql, running_stock[pid])
                    )

                else:
                    sid = it["id_servicio"]
                    precio = service_price[sid]
                    subtotal = round(precio * cantidad, 2)
                    total += subtotal
                    cur.execute(
                        'INSERT INTO detalle_factura (id_factura, id_producto, id_servicio, cantidad, precio_unitario, subtotal) '
                        'VALUES (%s, %s, %s, %s, %s, %s)',
                        (factura_id, None, sid, cantidad, precio, subtotal)
                    )

           
            cur.execute('UPDATE factura SET total = %s WHERE id = %s', (round(total, 2), factura_id))
            mysql.connection.commit()

            return jsonify({"factura_id": factura_id, "total": round(total, 2)}), 201

        except Exception:
            mysql.connection.rollback()
            raise
        finally:
            cur.close()

    except Exception as e:
        return jsonify({"message": "Error interno"}), 500



@app.route('/usuarios/<int:id_user>/factura/<int:id_factura>', methods=['PUT'])
@token_required
@user_resource_param("id_user")
@factura_resource
def update_factura(id_user, id_factura):
    body = request.get_json(force=True) or {}
    fecha_emision = (body.get("fecha_emision") or "").strip()
    id_clientes   = body.get("id_clientes")

    if not fecha_emision or not id_clientes:
        return jsonify({"message": "fecha_emision e id_clientes son obligatorios"}), 400

    try:
        if len(fecha_emision) == 10:
            _dt = datetime.strptime(fecha_emision, "%Y-%m-%d")
        else:
            _dt = datetime.fromisoformat(fecha_emision)
        fecha_emision_sql = _dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return jsonify({"message": "fecha_emision inválida"}), 400

    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        
        cur.execute(
            'SELECT id FROM clientes WHERE id = %s AND id_usuario = %s AND activo = 1',
            (id_clientes, id_user)
        )
        if not cur.fetchone():
            return jsonify({"message": "Cliente inexistente, inactivo o de otro usuario"}), 403

        cur.execute(
            "UPDATE factura SET fecha_emision = %s, id_clientes = %s, id_usuario = %s WHERE id = %s",
            (fecha_emision_sql, id_clientes, id_user, id_factura)
        )
        mysql.connection.commit()
        return jsonify({
            "factura_id": id_factura,
            "fecha_emision": fecha_emision_sql,
            "id_clientes": id_clientes
        }), 200
    finally:
        cur.close()



@app.route('/usuarios/<int:id_user>/factura/<int:id_factura>', methods=['DELETE'])
@token_required
@user_resource_param("id_user")
@factura_resource
def remove_factura(id_user, id_factura):
    try:
        cur = mysql.connection.cursor(cursors.DictCursor)
        try:
            cur.execute('DELETE FROM detalle_factura WHERE id_factura = %s', (id_factura,))
            cur.execute('DELETE FROM factura WHERE id = %s', (id_factura,))
            mysql.connection.commit()
            return jsonify({"message": "Factura eliminada", "factura_id": id_factura}), 200
        except Exception:
            mysql.connection.rollback()
            raise
        finally:
            cur.close()
    except Exception as e:
        return jsonify({"message": "Error interno"}), 500



@app.route('/usuarios/<int:id_user>/factura/<int:id_factura>', methods=['GET'])
@token_required
@user_resource_param("id_user")
@factura_resource
def consultar_factura(id_user, id_factura):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
   
        cur.execute('''
            SELECT f.id, f.fecha_emision, f.id_clientes, f.id_usuario, f.total,
                   c.nombre AS cliente_nombre, c.cuit AS cliente_cuit
            FROM factura f
            INNER JOIN clientes c ON f.id_clientes = c.id
            WHERE f.id = %s AND f.id_usuario = %s
        ''', (id_factura, id_user))
        f = cur.fetchone()
        if not f:
            return jsonify({"message": "Factura no encontrada"}), 404

        factura_info = Factura(f).to_json() if hasattr(Factura, "to_json") else {
            "id": f["id"],
            "fecha_emision": f["fecha_emision"],
            "id_clientes": f["id_clientes"],
            "id_usuario": f["id_usuario"],
            "total": f["total"],
        }

        cliente_nombre = f["cliente_nombre"]
        cliente_cuit   = f["cliente_cuit"]

  
        cur.execute('SELECT * FROM detalle_factura WHERE id_factura = %s', (id_factura,))
        data_detalle = cur.fetchall()
        detalle_list = [
            DetalleFactura(row).to_json() if hasattr(DetalleFactura, "to_json") else {
                "id_factura": row["id_factura"],
                "id_producto": row["id_producto"],
                "id_servicio": row["id_servicio"],
                "cantidad": float(row["cantidad"]),
                "precio_unitario": float(row["precio_unitario"]),
                "subtotal": float(row["subtotal"]),
            }
            for row in data_detalle
        ]

     
        productos_servicios_list = []
        for d in detalle_list:
            if d.get("id_producto"):
                cur.execute('SELECT * FROM productos WHERE id = %s', (d["id_producto"],))
                p = cur.fetchone()
                if p:
                    productos_servicios_list.append(
                        Producto(p).to_json() if hasattr(Producto, "to_json") else p
                    )
            elif d.get("id_servicio"):
                cur.execute('SELECT * FROM servicios WHERE id = %s', (d["id_servicio"],))
                s = cur.fetchone()
                if s:
                    productos_servicios_list.append(
                        Servicio(s).to_json() if hasattr(Servicio, "to_json") else s
                    )

        return jsonify({
            "factura": factura_info,
            "cliente": {
                "nombre_cliente": cliente_nombre,
                "cuit_cliente": cliente_cuit
            },
            "detalles": detalle_list,
            "productos_servicios": productos_servicios_list,
            "total": float(factura_info.get("total", 0))
        }), 200
    finally:
        cur.close()


@app.route('/usuarios/<int:id_user>/factura/total', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_total_facturas(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        f_from, f_to = parse_from_to(request.args)
        params = [id_user]
        where = "WHERE id_usuario = %s"
        if f_from and f_to:
            where += " AND fecha_emision BETWEEN %s AND %s"
            params.extend([f_from, f_to])
        elif f_from:
            where += " AND fecha_emision >= %s"
            params.append(f_from)
        elif f_to:
            where += " AND fecha_emision <= %s"
            params.append(f_to)

        cur.execute(f'SELECT COALESCE(SUM(total),0) AS total FROM factura {where}', tuple(params))
        total_value = float(cur.fetchone()["total"] or 0)
        return jsonify({"total_facturas_usuario": total_value}), 200
    finally:
        cur.close()




@app.route('/usuarios/<int:id_user>/factura/cantidad', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_cantidad_facturas(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        f_from, f_to = parse_from_to(request.args)
        params = [id_user]
        where = "WHERE id_usuario = %s"
        if f_from and f_to:
            where += " AND fecha_emision BETWEEN %s AND %s"
            params.extend([f_from, f_to])
        elif f_from:
            where += " AND fecha_emision >= %s"
            params.append(f_from)
        elif f_to:
            where += " AND fecha_emision <= %s"
            params.append(f_to)

        cur.execute(f'SELECT COUNT(*) AS qty FROM factura {where}', tuple(params))
        cantidad = int(cur.fetchone()["qty"])
        return jsonify({"cantidad_facturas_usuario": cantidad}), 200
    finally:
        cur.close()



@app.route('/usuarios/<int:id_user>/factura/producto-mas-vendido', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_producto_mas_vendido(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        f_from, f_to = parse_from_to(request.args)
        params = [id_user]
        date_filter = ""
        if f_from and f_to:
            date_filter = " AND F.fecha_emision BETWEEN %s AND %s"
            params.extend([f_from, f_to])
        elif f_from:
            date_filter = " AND F.fecha_emision >= %s"
            params.append(f_from)
        elif f_to:
            date_filter = " AND F.fecha_emision <= %s"
            params.append(f_to)

        cur.execute(f'''
            SELECT P.nombre AS nombre, COALESCE(SUM(DF.cantidad),0) AS cantidad_vendida
            FROM detalle_factura DF
            JOIN productos P ON DF.id_producto = P.id
            JOIN factura F ON DF.id_factura = F.id
            WHERE F.id_usuario = %s AND DF.id_producto IS NOT NULL {date_filter}
            GROUP BY DF.id_producto, P.nombre
            ORDER BY cantidad_vendida DESC
            LIMIT 1
        ''', tuple(params))
        row = cur.fetchone()
        if not row:
            return jsonify({"message": "Sin ventas en el rango"}), 404
        return jsonify({
            "producto_mas_vendido": row["nombre"],
            "cantidad_vendida": float(row["cantidad_vendida"] or 0)
        }), 200
    finally:
        cur.close()




@app.route('/usuarios/<int:id_user>/factura/servicio-mas-vendido', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_servicio_mas_vendido(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        f_from, f_to = parse_from_to(request.args)

        params = [id_user]
        date_filter = ""
        if f_from and f_to:
            date_filter = " AND F.fecha_emision BETWEEN %s AND %s"
            params.extend([f_from, f_to])
        elif f_from:
            date_filter = " AND F.fecha_emision >= %s"
            params.append(f_from)
        elif f_to:
            date_filter = " AND F.fecha_emision <= %s"
            params.append(f_to)

        cur.execute(f'''
            SELECT S.nombre AS nombre, COALESCE(SUM(DF.cantidad),0) AS cantidad_vendida
            FROM detalle_factura DF
            JOIN servicios S ON DF.id_servicio = S.id
            JOIN factura  F  ON DF.id_factura  = F.id
            WHERE F.id_usuario = %s
              AND DF.id_servicio IS NOT NULL
              {date_filter}
            GROUP BY DF.id_servicio, S.nombre
            ORDER BY cantidad_vendida DESC
            LIMIT 1
        ''', tuple(params))

        row = cur.fetchone()
        if not row:
            return jsonify({"message": "Sin servicios vendidos en el rango"}), 404

        return jsonify({
            "servicio_mas_vendido": row["nombre"],
            "cantidad_vendida": float(row["cantidad_vendida"] or 0)
        }), 200
    finally:
        cur.close()




@app.route('/usuarios/<int:id_user>/facturas/total', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_total_facturas_creadas(id_user):
    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute('SELECT COUNT(*) AS qty FROM factura WHERE id_usuario = %s', (id_user,))
        total_facturas = int(cur.fetchone()["qty"])
        return jsonify({"total_facturas_creadas": total_facturas}), 200
    finally:
        cur.close()



@app.route('/usuarios/<int:id_user>/facturas/detalles', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_detalles_facturas_paginadas(id_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 5
        if page < 1: page = 1
        if per_page < 1 or per_page > 100: per_page = 5
        offset = (page - 1) * per_page

        cur = mysql.connection.cursor(cursors.DictCursor)
        try:
            cur.execute('SELECT COUNT(*) AS total FROM factura WHERE id_usuario = %s', (id_user,))
            total_facturas = int(cur.fetchone()["total"])

            cur.execute('''
                SELECT f.id, f.fecha_emision, f.id_clientes, f.total, c.nombre AS cliente_nombre
                FROM factura f
                JOIN clientes c ON f.id_clientes = c.id
                WHERE f.id_usuario = %s
                ORDER BY f.id DESC
                LIMIT %s OFFSET %s
            ''', (id_user, per_page, offset))
            rows = cur.fetchall()

            factura_list = [{
                "factura_id": r["id"],
                "fecha_emision": r["fecha_emision"],
                "nombre_cliente": r["cliente_nombre"],
                "total": float(r["total"] or 0)
            } for r in rows]

            total_pages = ceil(total_facturas / per_page) if per_page else 1
            return jsonify({
                "total_pages": total_pages,
                "current_page": page,
                "facturas_detalles": factura_list
            }), 200
        finally:
            cur.close()
    except Exception as e:
        return jsonify({"message": "Error interno"}), 500



@app.route('/usuarios/<int:id_user>/movimientos-recientes', methods=['GET'])
@token_required
@user_resource_param("id_user")
def get_movimientos_recientes(id_user):


    try:
        limit  = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
    except ValueError:
        return jsonify({"message": "limit/offset inválidos"}), 400

    if limit < 1:  limit = 10
    if limit > 100: limit = 100
    if offset < 0: offset = 0

    f_from, f_to = parse_from_to(request.args)


    date_filter = ""
    date_params: list = []
    if f_from and f_to:
        date_filter = " AND F.fecha_emision BETWEEN %s AND %s"
        date_params.extend([f_from, f_to])
    elif f_from:
        date_filter = " AND F.fecha_emision >= %s"
        date_params.append(f_from)
    elif f_to:
        date_filter = " AND F.fecha_emision <= %s"
        date_params.append(f_to)

    sql = f"""
    (
      SELECT 
        F.fecha_emision         AS fecha,
        F.id                    AS factura_id,
        'producto'              AS tipo,
        P.id                    AS item_id,
        P.nombre                AS item_nombre,
        DF.cantidad             AS cantidad,
        DF.precio_unitario      AS precio_unitario,
        DF.subtotal             AS subtotal,
        C.nombre                AS cliente
      FROM detalle_factura DF
      JOIN factura   F ON DF.id_factura  = F.id
      JOIN productos P ON DF.id_producto = P.id
      JOIN clientes  C ON F.id_clientes  = C.id
      WHERE F.id_usuario = %s
        AND DF.id_producto IS NOT NULL
        {date_filter}
    )
    UNION ALL
    (
      SELECT 
        F.fecha_emision,
        F.id,
        'servicio',
        S.id,
        S.nombre,
        DF.cantidad,
        DF.precio_unitario,
        DF.subtotal,
        C.nombre
      FROM detalle_factura DF
      JOIN factura   F ON DF.id_factura   = F.id
      JOIN servicios S ON DF.id_servicio  = S.id
      JOIN clientes  C ON F.id_clientes   = C.id
      WHERE F.id_usuario = %s
        AND DF.id_servicio IS NOT NULL
        {date_filter}
    )
    ORDER BY fecha DESC, factura_id DESC
    LIMIT %s OFFSET %s
    """


    params: list = [id_user] + date_params + [id_user] + date_params + [limit, offset]

    cur = mysql.connection.cursor(cursors.DictCursor)
    try:
        cur.execute(sql, tuple(params))
        rows = cur.fetchall() or []

        def _fmt_fecha(v):
            if isinstance(v, datetime):
       
                return v.strftime("%Y-%m-%d %H:%M:%S")
            return v

        out = []
        for r in rows:
            out.append({
                "fecha": _fmt_fecha(r.get("fecha")),
                "factura_id": int(r.get("factura_id")),
                "tipo": r.get("tipo"),  
                "item_id": int(r.get("item_id")) if r.get("item_id") is not None else None,
                "item_nombre": r.get("item_nombre"),
                "cantidad": float(r.get("cantidad") or 0),
                "precio_unitario": float(r.get("precio_unitario") or 0),
                "subtotal": float(r.get("subtotal") or 0),
                "cliente": r.get("cliente"),
            })

        return jsonify(out), 200
    except Exception as e:
        return jsonify({"message": f"movimientos-recientes: {str(e)}"}), 500
    finally:
        cur.close()