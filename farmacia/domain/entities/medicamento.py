from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class Medicamento:
    id_laboratorio: int
    codigo: str
    nombre: str
    precio: Decimal
    fecha_vencimiento: date
    stock: int = 0
    requiere_receta: bool = False
    descripcion: Optional[str] = None
    id_medicamento: Optional[int] = None

    def esta_vencido(self, hoy: date) -> bool:
        """Regla de negocio: un medicamento vencido no se puede vender (R2)."""
        return self.fecha_vencimiento < hoy
