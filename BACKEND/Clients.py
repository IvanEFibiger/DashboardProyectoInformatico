class Client:
    def __init__(self, client_id, nombre, email, direccion, id_usuario):
        self.client_id = client_id
        self.nombre = nombre
        self.email = email
        self.direccion = direccion
        self.id_usuario = id_usuario

    def to_dict(self):
        return {
            'client_id': self.client_id,
            'nombre': self.nombre,
            'email': self.email,
            'direccion': self.direccion,
            'id_usuario': self.id_usuario
        }