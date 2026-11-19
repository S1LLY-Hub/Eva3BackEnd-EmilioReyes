from typing import List, Optional

from farmacia.domain.entities import Laboratorio
from farmacia.domain.repositories import LaboratorioRepositorio
from farmacia.infrastructure.models import LaboratorioModel


def _a_entidad(m: LaboratorioModel) -> Laboratorio:
    return Laboratorio(id_laboratorio=m.id_laboratorio, nombre=m.nombre, pais=m.pais)


class LaboratorioRepositorioORM(LaboratorioRepositorio):
    def listar(self) -> List[Laboratorio]:
        return [_a_entidad(m) for m in LaboratorioModel.objects.order_by("nombre")]

    def obtener(self, id_laboratorio: int) -> Optional[Laboratorio]:
        m = LaboratorioModel.objects.filter(pk=id_laboratorio).first()
        return _a_entidad(m) if m else None

    def obtener_por_nombre(self, nombre: str) -> Optional[Laboratorio]:
        m = LaboratorioModel.objects.filter(nombre__iexact=nombre).first()
        return _a_entidad(m) if m else None

    def guardar(self, laboratorio: Laboratorio) -> Laboratorio:
        if laboratorio.id_laboratorio is None:
            m = LaboratorioModel.objects.create(nombre=laboratorio.nombre, pais=laboratorio.pais)
        else:
            m = LaboratorioModel.objects.get(pk=laboratorio.id_laboratorio)
            m.nombre, m.pais = laboratorio.nombre, laboratorio.pais
            m.save()
        return _a_entidad(m)

    def eliminar(self, id_laboratorio: int) -> None:
        LaboratorioModel.objects.filter(pk=id_laboratorio).delete()
