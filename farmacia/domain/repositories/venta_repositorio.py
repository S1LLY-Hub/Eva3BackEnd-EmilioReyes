from abc import ABC, abstractmethod
from typing import List, Optional

from farmacia.domain.entities import Venta


class VentaRepositorio(ABC):
    @abstractmethod
    def listar(self) -> List[Venta]: ...

    @abstractmethod
    def obtener(self, id_venta: int) -> Optional[Venta]: ...

    @abstractmethod
    def existe_por_cliente(self, id_cliente: int) -> bool:
        """Para el borrado protegido de clientes."""

    @abstractmethod
    def guardar(self, venta: Venta) -> Venta: ...

    @abstractmethod
    def eliminar(self, id_venta: int) -> None: ...
