from dataclasses import dataclass
from decimal import Decimal


@dataclass
class DetalleVenta:
    """Clave compuesta: (id_venta, id_medicamento). No tiene id propio."""
    id_venta: int
    id_medicamento: int
    cantidad: int
    precio_unitario: Decimal

    @property
    def subtotal(self) -> Decimal:
        # En Oracle es una columna VIRTUAL; en el dominio se calcula igual.
        return self.cantidad * self.precio_unitario
