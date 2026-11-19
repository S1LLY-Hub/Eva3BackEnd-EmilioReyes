from abc import ABC, abstractmethod
from typing import List

from farmacia.domain.entities import DetalleVenta


class DetalleVentaRepositorio(ABC):
    @abstractmethod
    def listar_por_venta(self, id_venta: int) -> List[DetalleVenta]: ...

    @abstractmethod
    def existe_por_medicamento(self, id_medicamento: int) -> bool:
        """Para el borrado protegido de medicamentos."""

    @abstractmethod
    def guardar(self, detalle: DetalleVenta) -> DetalleVenta: ...

    @abstractmethod
    def eliminar(self, id_venta: int, id_medicamento: int) -> None: ...
