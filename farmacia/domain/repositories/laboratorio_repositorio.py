from abc import ABC, abstractmethod
from typing import List, Optional

from farmacia.domain.entities import Laboratorio


class LaboratorioRepositorio(ABC):
    """Puerto de salida: lo implementa la infraestructura."""

    @abstractmethod
    def listar(self) -> List[Laboratorio]: ...

    @abstractmethod
    def obtener(self, id_laboratorio: int) -> Optional[Laboratorio]: ...

    @abstractmethod
    def obtener_por_nombre(self, nombre: str) -> Optional[Laboratorio]: ...

    @abstractmethod
    def guardar(self, laboratorio: Laboratorio) -> Laboratorio:
        """Inserta (id None) o actualiza (id presente). Devuelve la entidad guardada."""

    @abstractmethod
    def eliminar(self, id_laboratorio: int) -> None: ...
