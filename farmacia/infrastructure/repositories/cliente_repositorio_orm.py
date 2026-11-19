from typing import List, Optional

from farmacia.domain.entities import Cliente
from farmacia.domain.repositories import ClienteRepositorio
from farmacia.infrastructure.models import ClienteModel


def _a_entidad(m: ClienteModel) -> Cliente:
    return Cliente(id_cliente=m.id_cliente, rut=m.rut, nombre=m.nombre, email=m.email,
                   telefono=m.telefono, fecha_registro=m.fecha_registro)


class ClienteRepositorioORM(ClienteRepositorio):
    def listar(self) -> List[Cliente]:
        return [_a_entidad(m) for m in ClienteModel.objects.order_by("nombre")]

    def obtener(self, id_cliente: int) -> Optional[Cliente]:
        m = ClienteModel.objects.filter(pk=id_cliente).first()
        return _a_entidad(m) if m else None

    def obtener_por_rut(self, rut: str) -> Optional[Cliente]:
        m = ClienteModel.objects.filter(rut=rut).first()
        return _a_entidad(m) if m else None

    def obtener_por_email(self, email: str) -> Optional[Cliente]:
        m = ClienteModel.objects.filter(email__iexact=email).first()
        return _a_entidad(m) if m else None

    def guardar(self, cliente: Cliente) -> Cliente:
        if cliente.id_cliente is None:
            m = ClienteModel.objects.create(rut=cliente.rut, nombre=cliente.nombre,
                                            email=cliente.email, telefono=cliente.telefono)
            m.refresh_from_db()  # trae fecha_registro puesta por Oracle
        else:
            m = ClienteModel.objects.get(pk=cliente.id_cliente)
            m.rut, m.nombre, m.email, m.telefono = (cliente.rut, cliente.nombre,
                                                    cliente.email, cliente.telefono)
            m.save()
        return _a_entidad(m)

    def eliminar(self, id_cliente: int) -> None:
        ClienteModel.objects.filter(pk=id_cliente).delete()
