# api/models/factura.py
from typing import Any, Dict, Iterable, Optional
from datetime import date, datetime

class Factura:
    __slots__ = ("id", "fecha_emision", "id_clientes", "id_usuario", "total")

    def __init__(
        self,
        row: Any,
        *,
        id: Optional[int] = None,
        fecha_emision: Optional[Any] = None,
        id_clientes: Optional[int] = None,
        id_usuario: Optional[int] = None,
        total: Optional[float] = None,
    ):

        self.id = None
        self.fecha_emision = None
        self.id_clientes = None
        self.id_usuario = None
        self.total = None

        if isinstance(row, dict):
            self.id            = row.get("id") or row.get("factura_id")
            self.fecha_emision = row.get("fecha_emision")

            self.id_clientes   = row.get("id_clientes") or row.get("id_cliente")
            self.id_usuario    = row.get("id_usuario")
            self.total         = row.get("total")
        elif isinstance(row, Iterable):
            r = list(row)
    
            if len(r) >= 1: self.id = r[0]
            if len(r) >= 2: self.fecha_emision = r[1]
            if len(r) >= 3: self.id_clientes = r[2]
            if len(r) >= 4: self.id_usuario = r[3]
            if len(r) >= 5: self.total = r[4]


        if id is not None: self.id = id
        if fecha_emision is not None: self.fecha_emision = fecha_emision
        if id_clientes is not None: self.id_clientes = id_clientes
        if id_usuario is not None: self.id_usuario = id_usuario
        if total is not None: self.total = total

    @staticmethod
    def _iso(dt: Any) -> Any:
        if isinstance(dt, (datetime, date)):
            return dt.isoformat()
        return dt

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "fecha_emision": self._iso(self.fecha_emision),
            "id_clientes": self.id_clientes,
            "id_usuario": self.id_usuario,
            "total": self.total,
        }
