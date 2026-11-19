from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class EstadoVenta(str, Enum):
    PENDIENTE = "pendiente"
    PAGADA = "pagada"
    ANULADA = "anulada"


@dataclass
class Venta:
    id_cliente: int
    fecha: Optional[datetime] = None
    numero_receta: Optional[str] = None
    total: Decimal = Decimal("0")
    estado: EstadoVenta = EstadoVenta.PENDIENTE
    id_venta: Optional[int] = None
