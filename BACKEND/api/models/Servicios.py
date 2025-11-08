# api/models/Servicios.py
from typing import Any, Dict, Iterable, Optional

class Servicio:
    __slots__ = ("id", "nombre", "descripcion", "precio", "id_usuario", "activo")

    def __init__(
        self,
        row: Any,
        *,
        id: Optional[int] = None,
        nombre: Optional[str] = None,
        descripcion: Optional[str] = None,
        precio: Optional[float] = None,
        id_usuario: Optional[int] = None,
        activo: Optional[int] = None,
    ):
      
        self.id = None
        self.nombre = None
        self.descripcion = None
        self.precio = None
        self.id_usuario = None
        self.activo = None

        if isinstance(row, dict):
            self.id          = row.get("id") or row.get("servicio_id")
            self.nombre      = row.get("nombre")
            self.descripcion = row.get("descripcion")
            self.precio      = row.get("precio")
      
            self.id_usuario  = row.get("id_usuario") or row.get("id_usuarios")
            self.activo      = row.get("activo", self.activo)
        elif isinstance(row, Iterable):
            r = list(row)
        
            if len(r) >= 1: self.id = r[0]
            if len(r) >= 2: self.nombre = r[1]
            if len(r) >= 3: self.descripcion = r[2]
            if len(r) >= 4: self.precio = r[3]
            if len(r) >= 5: self.id_usuario = r[4]
            if len(r) >= 6: self.activo = r[5]


        if id is not None: self.id = id
        if nombre is not None: self.nombre = nombre
        if descripcion is not None: self.descripcion = descripcion
        if precio is not None: self.precio = precio
        if id_usuario is not None: self.id_usuario = id_usuario
        if activo is not None: self.activo = activo

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "id_usuario": self.id_usuario,
            "activo": self.activo,
        }
