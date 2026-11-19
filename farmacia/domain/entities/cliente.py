from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Cliente:
    rut: str
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    fecha_registro: Optional[datetime] = None
    id_cliente: Optional[int] = None
