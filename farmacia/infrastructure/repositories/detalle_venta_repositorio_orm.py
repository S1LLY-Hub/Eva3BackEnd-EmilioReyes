from typing import List

from farmacia.domain.entities import DetalleVenta
from farmacia.domain.repositories import DetalleVentaRepositorio
from farmacia.infrastructure.models import DetalleVentaModel


def _a_entidad(m: DetalleVentaModel) -> DetalleVenta:
    return DetalleVenta(id_venta=m.venta_id, id_medicamento=m.medicamento_id,
                        cantidad=m.cantidad, precio_unitario=m.precio_unitario)


class DetalleVentaRepositorioORM(DetalleVentaRepositorio):
    def listar_por_venta(self, id_venta: int) -> List[DetalleVenta]:
        return [_a_entidad(m) for m in DetalleVentaModel.objects.filter(venta_id=id_venta)]

    def existe_por_medicamento(self, id_medicamento: int) -> bool:
        return DetalleVentaModel.objects.filter(medicamento_id=id_medicamento).exists()

    def guardar(self, detalle: DetalleVenta) -> DetalleVenta:
        DetalleVentaModel.objects.update_or_create(
            venta_id=detalle.id_venta, medicamento_id=detalle.id_medicamento,
            defaults=dict(cantidad=detalle.cantidad, precio_unitario=detalle.precio_unitario),
        )
        return detalle

    def eliminar(self, id_venta: int, id_medicamento: int) -> None:
        DetalleVentaModel.objects.filter(venta_id=id_venta, medicamento_id=id_medicamento).delete()
