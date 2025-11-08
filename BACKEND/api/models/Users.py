# api/models/Users.py
from typing import Any, Dict, Iterable, Optional

class User:
    __slots__ = ("id", "user", "email", "password", "activo")

    def __init__(
        self,
        row: Any,
        *,
        id: Optional[int] = None,
        user: Optional[str] = None,      
        email: Optional[str] = None,
        password: Optional[str] = None,  
        activo: Optional[int] = None,
    ):
        
        self.id = None
        self.user = None
        self.email = None
        self.password = None
        self.activo = None

        if isinstance(row, dict):
            self.id       = row.get("id") or row.get("user_id")
            self.user     = row.get("user") or row.get("username") or row.get("nombre")
            self.email    = row.get("email")
            self.password = row.get("password")
            self.activo   = row.get("activo", self.activo)
        elif isinstance(row, Iterable):
            r = list(row)
           
            if len(r) >= 1: self.id = r[0]
            if len(r) >= 2: self.user = r[1]
            if len(r) >= 3: self.email = r[2]
            if len(r) >= 4: self.password = r[3]
            if len(r) >= 5: self.activo = r[4]


        if id is not None: self.id = id
        if user is not None: self.user = user
        if email is not None: self.email = email
        if password is not None: self.password = password
        if activo is not None: self.activo = activo

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user": self.user,
            "email": self.email,
            "activo": self.activo,
        }


    def to_internal(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user": self.user,
            "email": self.email,
            "password": self.password,
            "activo": self.activo,
        }
