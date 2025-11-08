# api/models/movimiento_stock.py
from typing import Any, Dict, Iterable, Optional
from datetime import date, datetime

class MovimientoStock:
    __slots__ = ("id", "producto_id", "tipo", "cantidad", "fecha", "stock_real")

    def __init__(
        self,
        row: Any,
        *,
        id: Optional[int] = None,
        producto_id: Optional[int] = None,
        tipo: Optional[str] = None,
        cantidad: Optional[int] = None,
        fecha: Optional[Any] = None,
        stock_real: Optional[int] = None,
    ):
        self.id = None
        self.producto_id = None
        self.tipo = None
        self.cantidad = None
        self.fecha = None
        self.stock_real = None

        if isinstance(row, dict):
            self.id          = row.get("id")
            self.producto_id = row.get("producto_id")
            self.tipo        = row.get("tipo")
            self.cantidad    = row.get("cantidad")
            self.fecha       = row.get("fecha")
            self.stock_real  = row.get("stock_real")
        elif isinstance(row, Iterable):
            r = list(row)
            if len(r) >= 1: self.id = r[0]
            if len(r) >= 2: self.producto_id = r[1]
            if len(r) >= 3: self.tipo = r[2]
            if len(r) >= 4: self.cantidad = r[3]
            if len(r) >= 5: self.fecha = r[4]
            if len(r) >= 6: self.stock_real = r[5]

        if id is not None: self.id = id
        if producto_id is not None: self.producto_id = producto_id
        if tipo is not None: self.tipo = tipo
        if cantidad is not None: self.cantidad = cantidad
        if fecha is not None: self.fecha = fecha
        if stock_real is not None: self.stock_real = stock_real

    @staticmethod
    def _iso(dt: Any) -> Any:
        if isinstance(dt, (datetime, date)):
            return dt.isoformat()
        return dt

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "producto_id": self.producto_id,
            "tipo": self.tipo,
            "cantidad": self.cantidad,
            "fecha": self._iso(self.fecha),
            "stock_real": self.stock_real,
        }
