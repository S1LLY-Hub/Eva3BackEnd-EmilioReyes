from decimal import Decimal
from typing import List, Optional

from farmacia.domain.entities import EstadoVenta, Venta
from farmacia.domain.repositories import VentaRepositorio
from farmacia.infrastructure.models import VentaModel


def _a_entidad(m: VentaModel) -> Venta:
    return Venta(id_venta=m.id_venta, id_cliente=m.cliente_id, fecha=m.fecha,
                 numero_receta=m.numero_receta, total=Decimal(m.total),
                 estado=EstadoVenta(m.estado))


class VentaRepositorioORM(VentaRepositorio):
    def listar(self) -> List[Venta]:
        return [_a_entidad(m) for m in VentaModel.objects.order_by("-id_venta")]

    def obtener(self, id_venta: int) -> Optional[Venta]:
        m = VentaModel.objects.filter(pk=id_venta).first()
        return _a_entidad(m) if m else None

    def existe_por_cliente(self, id_cliente: int) -> bool:
        return VentaModel.objects.filter(cliente_id=id_cliente).exists()

    def guardar(self, venta: Venta) -> Venta:
        datos = dict(cliente_id=venta.id_cliente, numero_receta=venta.numero_receta,
                     total=venta.total, estado=venta.estado.value)
        if venta.id_venta is None:
            m = VentaModel.objects.create(**datos)
            m.refresh_from_db()  # trae fecha puesta por Oracle
        else:
            m = VentaModel.objects.get(pk=venta.id_venta)
            for campo, valor in datos.items():
                setattr(m, campo, valor)
            m.save()
        return _a_entidad(m)

    def eliminar(self, id_venta: int) -> None:
        VentaModel.objects.filter(pk=id_venta).delete()
