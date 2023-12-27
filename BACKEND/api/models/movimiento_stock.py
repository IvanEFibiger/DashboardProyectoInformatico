class MovimientoStock:
    def __init__(self, row):
        self._producto_id = row[0]
        self._tipo = row[1]
        self._cantidad = row[2]
        self._fecha = row[3]
        self._stock_real = row[4]


    def to_json(self):
        return {
            'producto_id': self._producto_id,
            'tipo': self._tipo,
            'cantidad': self._cantidad,
            'fecha': self._fecha,
            'stock_real': self._stock_real
        }

