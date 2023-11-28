class Servicio:
    def __init__(self, row):
        self._servicio_id = row[0]
        self._nombre = row[1]
        self._descripcion = row[2]
        self._precio = row [3]
        self._id_usuarios = row[4]

    def to_json(self):
        return {
            'servicio_id': self._servicio_id,
            'nombre': self._nombre,
            'descripcion': self._descripcion,
            'precio': self._precio,
            'id_usuario': self._id_usuarios
        }