from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class EstadoVenta(str, Enum):
    PENDIENTE = "pendiente"
    PAGADA = "pagada"
    ANULADA = "anulada"


# Maquina de estados: de donde se puede ir desde cada estado.
TRANSICIONES_VALIDAS = {
    EstadoVenta.PENDIENTE: {EstadoVenta.PAGADA, EstadoVenta.ANULADA},
    EstadoVenta.PAGADA: {EstadoVenta.ANULADA},
    EstadoVenta.ANULADA: set(),  # estado final
}


@dataclass
class Venta:
    id_cliente: int
    fecha: Optional[datetime] = None
    numero_receta: Optional[str] = None
    total: Decimal = Decimal("0")
    estado: EstadoVenta = EstadoVenta.PENDIENTE
    id_venta: Optional[int] = None

    def puede_pasar_a(self, nuevo: EstadoVenta) -> bool:
        return nuevo in TRANSICIONES_VALIDAS[self.estado]