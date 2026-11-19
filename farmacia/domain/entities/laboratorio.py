from dataclasses import dataclass
from typing import Optional


@dataclass
class Laboratorio:
    nombre: str
    pais: str
    id_laboratorio: Optional[int] = None
