class Factura:
    def __init__(self, row):
        self._factura_id = row[0]
        self._fecha_emision = row[1]
        self._id_clientes = row[2]
        self._id_usuario = row[3]

    def to_json(self):
        return {
            'factura_id': self._factura_id,
            'fecha_emision': self._fecha_emision,
            'id_clientes': self._id_clientes,
            'id_usuario': self._id_usuario
        }