# api/models/Productos.py
from typing import Any, Dict, Iterable, Optional

class Producto:
    __slots__ = ("id", "nombre", "descripcion", "precio", "cantidad", "id_usuario", "activo")

    def __init__(
        self,
        row: Any,
        *,
        id: Optional[int] = None,
        nombre: Optional[str] = None,
        descripcion: Optional[str] = None,
        precio: Optional[float] = None,
        cantidad: Optional[int] = None,
        id_usuario: Optional[int] = None,
        activo: Optional[int] = None,
    ):
        self.id = None
        self.nombre = None
        self.descripcion = None
        self.precio = None
        self.cantidad = None
        self.id_usuario = None
        self.activo = None

        if isinstance(row, dict):
            self.id          = row.get("id") or row.get("producto_id")
            self.nombre      = row.get("nombre")
            self.descripcion = row.get("descripcion")
            self.precio      = row.get("precio")
            self.cantidad    = row.get("cantidad")
            self.id_usuario  = row.get("id_usuario")
            self.activo      = row.get("activo", self.activo)
        elif isinstance(row, Iterable):
            r = list(row)
            if len(r) >= 1: self.id = r[0]
            if len(r) >= 2: self.nombre = r[1]
            if len(r) >= 3: self.descripcion = r[2]
            if len(r) >= 4: self.precio = r[3]
            if len(r) >= 5: self.cantidad = r[4]
            if len(r) >= 6: self.id_usuario = r[5]
            if len(r) >= 7: self.activo = r[6]

        if id is not None: self.id = id
        if nombre is not None: self.nombre = nombre
        if descripcion is not None: self.descripcion = descripcion
        if precio is not None: self.precio = precio
        if cantidad is not None: self.cantidad = cantidad
        if id_usuario is not None: self.id_usuario = id_usuario
        if activo is not None: self.activo = activo

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "cantidad": self.cantidad,
            "id_usuario": self.id_usuario,
            "activo": self.activo,
        }
