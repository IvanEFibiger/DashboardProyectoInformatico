class MovimientoStock:
    def __init__(self, row):
        self.producto_id = row[0]
        self.tipo = row[1]
        self.cantidad = row[2]
        self.fecha = row[3]

