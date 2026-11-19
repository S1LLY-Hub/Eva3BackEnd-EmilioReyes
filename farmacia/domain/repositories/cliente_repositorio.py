from abc import ABC, abstractmethod
from typing import List, Optional

from farmacia.domain.entities import Cliente


class ClienteRepositorio(ABC):
    @abstractmethod
    def listar(self) -> List[Cliente]: ...

    @abstractmethod
    def obtener(self, id_cliente: int) -> Optional[Cliente]: ...

    @abstractmethod
    def obtener_por_rut(self, rut: str) -> Optional[Cliente]: ...

    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[Cliente]: ...

    @abstractmethod
    def guardar(self, cliente: Cliente) -> Cliente: ...

    @abstractmethod
    def eliminar(self, id_cliente: int) -> None: ...
