class Clientes:
    def __init__(self, row):
        self._cliente_id = row[0]
        self._nombre = row[1]
        self._email = row[2]
        self._direccion = row[3]
        self._cuit = row[4]
        self._id_usuario = row[5]

    def to_json(self):
        return {
            'cliente_id': self._cliente_id,
            'nombre': self._nombre,
            'email': self._email,
            'direccion': self._direccion,
            'cuit': self._cuit,
            'id_usuario': self._id_usuario
        }