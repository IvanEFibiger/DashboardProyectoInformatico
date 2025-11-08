# api/models/Clientes.py
from typing import Any, Dict, Iterable, Optional

class Clientes:
    __slots__ = ("id", "nombre", "email", "direccion", "cuit", "id_usuario", "activo")

    def __init__(
        self,
        row: Any,
        *,
        id: Optional[int] = None,
        nombre: Optional[str] = None,
        email: Optional[str] = None,
        direccion: Optional[str] = None,
        cuit: Optional[str] = None,
        id_usuario: Optional[int] = None,
        activo: Optional[int] = None,
    ):
        """
        row puede ser una tupla (orden de columnas estándar)
        o un dict (cursor dictionary=True). Los kwargs pisan lo que venga en row.
        Orden esperado para tupla:
        (id, nombre, email, direccion, cuit, id_usuario, [activo])
        """
 
        self.id = None
        self.nombre = None
        self.email = None
        self.direccion = None
        self.cuit = None
        self.id_usuario = None
        self.activo = None

        if isinstance(row, dict):
            self.id         = row.get("id")
            self.nombre     = row.get("nombre")
            self.email      = row.get("email")
            self.direccion  = row.get("direccion")
            self.cuit       = row.get("cuit")
            self.id_usuario = row.get("id_usuario")
       
            self.activo     = row.get("activo", self.activo)
        elif isinstance(row, Iterable):
            r = list(row)

            if len(r) >= 1: self.id = r[0]
            if len(r) >= 2: self.nombre = r[1]
            if len(r) >= 3: self.email = r[2]
            if len(r) >= 4: self.direccion = r[3]
            if len(r) >= 5: self.cuit = r[4]
            if len(r) >= 6: self.id_usuario = r[5]
            if len(r) >= 7: self.activo = r[6]
        else:
        
            pass

      
        if id is not None: self.id = id
        if nombre is not None: self.nombre = nombre
        if email is not None: self.email = email
        if direccion is not None: self.direccion = direccion
        if cuit is not None: self.cuit = cuit
        if id_usuario is not None: self.id_usuario = id_usuario
        if activo is not None: self.activo = activo

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "direccion": self.direccion,
            "cuit": self.cuit,
            "id_usuario": self.id_usuario,
            "activo": self.activo,
        }
