# api/models/detalle_factura.py
from typing import Any, Dict, Iterable, Optional

class DetalleFactura:
    __slots__ = ("id", "id_factura", "id_producto", "id_servicio",
                 "cantidad", "precio_unitario", "subtotal")

    def __init__(
        self,
        row: Any,
        *,
        id: Optional[int] = None,
        id_factura: Optional[int] = None,
        id_producto: Optional[int] = None,
        id_servicio: Optional[int] = None,
        cantidad: Optional[int] = None,
        precio_unitario: Optional[float] = None,
        subtotal: Optional[float] = None,
    ):
      
        self.id = None
        self.id_factura = None
        self.id_producto = None
        self.id_servicio = None
        self.cantidad = None
        self.precio_unitario = None
        self.subtotal = None

        if isinstance(row, dict):
            self.id              = row.get("id")
            self.id_factura      = row.get("id_factura")
            self.id_producto     = row.get("id_producto")
            self.id_servicio     = row.get("id_servicio")
            self.cantidad        = row.get("cantidad")
            self.precio_unitario = row.get("precio_unitario")
            self.subtotal        = row.get("subtotal")
        elif isinstance(row, Iterable):
            r = list(row)
       
            if len(r) >= 1: self.id = r[0]
            if len(r) >= 2: self.id_factura = r[1]
            if len(r) >= 3: self.id_producto = r[2]
            if len(r) >= 4: self.id_servicio = r[3]
            if len(r) >= 5: self.cantidad = r[4]
            if len(r) >= 6: self.precio_unitario = r[5]
            if len(r) >= 7: self.subtotal = r[6]


        if id is not None: self.id = id
        if id_factura is not None: self.id_factura = id_factura
        if id_producto is not None: self.id_producto = id_producto
        if id_servicio is not None: self.id_servicio = id_servicio
        if cantidad is not None: self.cantidad = cantidad
        if precio_unitario is not None: self.precio_unitario = precio_unitario
        if subtotal is not None: self.subtotal = subtotal

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "id_factura": self.id_factura,
            "id_producto": self.id_producto,
            "id_servicio": self.id_servicio,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "subtotal": self.subtotal,
        }
