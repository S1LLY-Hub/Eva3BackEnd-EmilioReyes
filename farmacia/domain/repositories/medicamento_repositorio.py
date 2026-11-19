from abc import ABC, abstractmethod
from typing import List, Optional

from farmacia.domain.entities import Medicamento


class MedicamentoRepositorio(ABC):
    @abstractmethod
    def listar(self) -> List[Medicamento]: ...

    @abstractmethod
    def obtener(self, id_medicamento: int) -> Optional[Medicamento]: ...

    @abstractmethod
    def obtener_por_codigo(self, codigo: str) -> Optional[Medicamento]: ...

    @abstractmethod
    def existe_por_laboratorio(self, id_laboratorio: int) -> bool:
        """Para el borrado protegido de laboratorios."""

    @abstractmethod
    def guardar(self, medicamento: Medicamento) -> Medicamento: ...

    @abstractmethod
    def eliminar(self, id_medicamento: int) -> None: ...
