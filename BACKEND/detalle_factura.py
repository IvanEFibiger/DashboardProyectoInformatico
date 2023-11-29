class DetalleFactura:
    def __init__(self, row):
        self._detalle_id = row[0]
        self._id_factura = row[1]
        self._id_producto = row[2]
        self._id_servicio = row[3]
        self._cantidad = row[4]
        self._precio_unitario = row[5]
        self._subtotal = row[6]

    def to_json(self):
        return {
            'detalle_id': self._detalle_id,
            'id_factura': self._id_factura,
            'id_producto': self._id_producto,
            'id_servicio': self._id_servicio,
            'cantidad': self._cantidad,
            'precio_unitario': self._precio_unitario,
            'subtotal': self._subtotal
        }