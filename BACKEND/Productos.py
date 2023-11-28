class Producto:
    def __init__(self, row):
        self._producto_id = row[0]
        self._nombre = row[1]
        self._descripcion = row[2]
        self._precio = row[3]
        self._cantidad = row[4]
        self._id_usuario = row [5]


    def to_json(self):
        return {
            'producto_id': self._producto_id,
            'nombre': self._nombre,
            'descripcion': self._descripcion,
            'precio': self._precio,
            'cantidad': self._cantidad,
            'id_usuario': self._id_usuario
        }