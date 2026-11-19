"""Casos de uso CRUD de Cliente. Solo dependen del dominio."""
from typing import List, Optional

from farmacia.domain.entities import Cliente
from farmacia.domain.exceptions import (
    CampoObligatorio,
    ClienteConVentas,
    ClienteDuplicado,
    ClienteNoEncontrado,
)
from farmacia.domain.repositories import ClienteRepositorio, VentaRepositorio


def _limpiar(valor: Optional[str]) -> Optional[str]:
    valor = (valor or "").strip()
    return valor or None


def _validar(rut: str, nombre: str) -> None:
    if not rut or not rut.strip():
        raise CampoObligatorio("El RUT es obligatorio.")
    if not nombre or not nombre.strip():
        raise CampoObligatorio("El nombre es obligatorio.")


def _verificar_duplicados(clientes: ClienteRepositorio, rut: str, email: Optional[str],
                          id_propio: Optional[int] = None) -> None:
    por_rut = clientes.obtener_por_rut(rut)
    if por_rut is not None and por_rut.id_cliente != id_propio:
        raise ClienteDuplicado(f"Ya existe un cliente con RUT {rut}.")
    if email:
        por_email = clientes.obtener_por_email(email)
        if por_email is not None and por_email.id_cliente != id_propio:
            raise ClienteDuplicado(f"Ya existe un cliente con email {email}.")


class CrearCliente:
    def __init__(self, clientes: ClienteRepositorio):
        self._clientes = clientes

    def ejecutar(self, rut: str, nombre: str, email: Optional[str] = None,
                 telefono: Optional[str] = None) -> Cliente:
        _validar(rut, nombre)
        rut, email = rut.strip(), _limpiar(email)
        _verificar_duplicados(self._clientes, rut, email)
        return self._clientes.guardar(
            Cliente(rut=rut, nombre=nombre.strip(), email=email, telefono=_limpiar(telefono))
        )


class ListarClientes:
    def __init__(self, clientes: ClienteRepositorio):
        self._clientes = clientes

    def ejecutar(self) -> List[Cliente]:
        return self._clientes.listar()


class ObtenerCliente:
    def __init__(self, clientes: ClienteRepositorio):
        self._clientes = clientes

    def ejecutar(self, id_cliente: int) -> Cliente:
        cliente = self._clientes.obtener(id_cliente)
        if cliente is None:
            raise ClienteNoEncontrado(f"No existe el cliente {id_cliente}.")
        return cliente


class ActualizarCliente:
    def __init__(self, clientes: ClienteRepositorio):
        self._clientes = clientes

    def ejecutar(self, id_cliente: int, rut: str, nombre: str, email: Optional[str] = None,
                 telefono: Optional[str] = None) -> Cliente:
        _validar(rut, nombre)
        cliente = self._clientes.obtener(id_cliente)
        if cliente is None:
            raise ClienteNoEncontrado(f"No existe el cliente {id_cliente}.")
        rut, email = rut.strip(), _limpiar(email)
        _verificar_duplicados(self._clientes, rut, email, id_propio=id_cliente)
        cliente.rut, cliente.nombre = rut, nombre.strip()
        cliente.email, cliente.telefono = email, _limpiar(telefono)
        return self._clientes.guardar(cliente)


class EliminarCliente:
    """Borrado protegido: no se elimina si tiene ventas."""

    def __init__(self, clientes: ClienteRepositorio, ventas: VentaRepositorio):
        self._clientes = clientes
        self._ventas = ventas

    def ejecutar(self, id_cliente: int) -> None:
        if self._clientes.obtener(id_cliente) is None:
            raise ClienteNoEncontrado(f"No existe el cliente {id_cliente}.")
        if self._ventas.existe_por_cliente(id_cliente):
            raise ClienteConVentas("No se puede eliminar: el cliente tiene ventas registradas.")
        self._clientes.eliminar(id_cliente)
