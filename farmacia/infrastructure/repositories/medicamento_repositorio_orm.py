from typing import List, Optional

from farmacia.domain.entities import Medicamento
from farmacia.domain.repositories import MedicamentoRepositorio
from farmacia.infrastructure.models import MedicamentoModel


def _a_entidad(m: MedicamentoModel) -> Medicamento:
    return Medicamento(
        id_medicamento=m.id_medicamento, id_laboratorio=m.laboratorio_id, codigo=m.codigo,
        nombre=m.nombre, descripcion=m.descripcion, precio=m.precio, stock=m.stock,
        requiere_receta=bool(m.requiere_receta), fecha_vencimiento=m.fecha_vencimiento,
    )


class MedicamentoRepositorioORM(MedicamentoRepositorio):
    def listar(self) -> List[Medicamento]:
        return [_a_entidad(m) for m in MedicamentoModel.objects.order_by("codigo")]

    def obtener(self, id_medicamento: int) -> Optional[Medicamento]:
        m = MedicamentoModel.objects.filter(pk=id_medicamento).first()
        return _a_entidad(m) if m else None

    def obtener_por_codigo(self, codigo: str) -> Optional[Medicamento]:
        m = MedicamentoModel.objects.filter(codigo=codigo).first()
        return _a_entidad(m) if m else None

    def existe_por_laboratorio(self, id_laboratorio: int) -> bool:
        return MedicamentoModel.objects.filter(laboratorio_id=id_laboratorio).exists()

    def guardar(self, medicamento: Medicamento) -> Medicamento:
        datos = dict(
            laboratorio_id=medicamento.id_laboratorio, codigo=medicamento.codigo,
            nombre=medicamento.nombre, descripcion=medicamento.descripcion,
            precio=medicamento.precio, stock=medicamento.stock,
            requiere_receta=medicamento.requiere_receta,
            fecha_vencimiento=medicamento.fecha_vencimiento,
        )
        if medicamento.id_medicamento is None:
            m = MedicamentoModel.objects.create(**datos)
        else:
            m = MedicamentoModel.objects.get(pk=medicamento.id_medicamento)
            for campo, valor in datos.items():
                setattr(m, campo, valor)
            m.save()
        return _a_entidad(m)

    def eliminar(self, id_medicamento: int) -> None:
        MedicamentoModel.objects.filter(pk=id_medicamento).delete()
