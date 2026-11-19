"""Casos de uso CRUD de Medicamento. Solo dependen del dominio."""
from datetime import date
from decimal import Decimal
from typing import List, Optional

from farmacia.domain.entities import Medicamento
from farmacia.domain.exceptions import (
    CampoObligatorio,
    LaboratorioNoEncontrado,
    MedicamentoConVentas,
    MedicamentoDuplicado,
    MedicamentoNoEncontrado,
    PrecioInvalido,
    StockInvalido,
)
from farmacia.domain.repositories import (
    DetalleVentaRepositorio,
    LaboratorioRepositorio,
    MedicamentoRepositorio,
)


def _validar(codigo: str, nombre: str, precio: Decimal, stock: int) -> None:
    if not codigo or not codigo.strip():
        raise CampoObligatorio("El codigo es obligatorio.")
    if not nombre or not nombre.strip():
        raise CampoObligatorio("El nombre es obligatorio.")
    if precio < 0:
        raise PrecioInvalido("El precio no puede ser negativo.")
    if stock < 0:
        raise StockInvalido("El stock no puede ser negativo.")


class CrearMedicamento:
    def __init__(self, medicamentos: MedicamentoRepositorio, laboratorios: LaboratorioRepositorio):
        self._medicamentos = medicamentos
        self._laboratorios = laboratorios

    def ejecutar(self, id_laboratorio: int, codigo: str, nombre: str, precio: Decimal,
                 fecha_vencimiento: date, stock: int = 0, requiere_receta: bool = False,
                 descripcion: Optional[str] = None) -> Medicamento:
        _validar(codigo, nombre, precio, stock)
        if self._laboratorios.obtener(id_laboratorio) is None:
            raise LaboratorioNoEncontrado(f"No existe el laboratorio {id_laboratorio}.")
        if self._medicamentos.obtener_por_codigo(codigo.strip()):
            raise MedicamentoDuplicado(f"Ya existe un medicamento con codigo '{codigo}'.")
        return self._medicamentos.guardar(Medicamento(
            id_laboratorio=id_laboratorio, codigo=codigo.strip(), nombre=nombre.strip(),
            precio=precio, fecha_vencimiento=fecha_vencimiento, stock=stock,
            requiere_receta=requiere_receta, descripcion=descripcion,
        ))


class ListarMedicamentos:
    def __init__(self, medicamentos: MedicamentoRepositorio):
        self._medicamentos = medicamentos

    def ejecutar(self) -> List[Medicamento]:
        return self._medicamentos.listar()


class ObtenerMedicamento:
    def __init__(self, medicamentos: MedicamentoRepositorio):
        self._medicamentos = medicamentos

    def ejecutar(self, id_medicamento: int) -> Medicamento:
        med = self._medicamentos.obtener(id_medicamento)
        if med is None:
            raise MedicamentoNoEncontrado(f"No existe el medicamento {id_medicamento}.")
        return med


class ActualizarMedicamento:
    def __init__(self, medicamentos: MedicamentoRepositorio, laboratorios: LaboratorioRepositorio):
        self._medicamentos = medicamentos
        self._laboratorios = laboratorios

    def ejecutar(self, id_medicamento: int, id_laboratorio: int, codigo: str, nombre: str,
                 precio: Decimal, fecha_vencimiento: date, stock: int = 0,
                 requiere_receta: bool = False, descripcion: Optional[str] = None) -> Medicamento:
        _validar(codigo, nombre, precio, stock)
        med = self._medicamentos.obtener(id_medicamento)
        if med is None:
            raise MedicamentoNoEncontrado(f"No existe el medicamento {id_medicamento}.")
        if self._laboratorios.obtener(id_laboratorio) is None:
            raise LaboratorioNoEncontrado(f"No existe el laboratorio {id_laboratorio}.")
        otro = self._medicamentos.obtener_por_codigo(codigo.strip())
        if otro is not None and otro.id_medicamento != id_medicamento:
            raise MedicamentoDuplicado(f"Ya existe un medicamento con codigo '{codigo}'.")
        med.id_laboratorio, med.codigo, med.nombre = id_laboratorio, codigo.strip(), nombre.strip()
        med.precio, med.fecha_vencimiento, med.stock = precio, fecha_vencimiento, stock
        med.requiere_receta, med.descripcion = requiere_receta, descripcion
        return self._medicamentos.guardar(med)


class EliminarMedicamento:
    """Borrado protegido: no se elimina si aparece en el detalle de una venta."""

    def __init__(self, medicamentos: MedicamentoRepositorio, detalles: DetalleVentaRepositorio):
        self._medicamentos = medicamentos
        self._detalles = detalles

    def ejecutar(self, id_medicamento: int) -> None:
        if self._medicamentos.obtener(id_medicamento) is None:
            raise MedicamentoNoEncontrado(f"No existe el medicamento {id_medicamento}.")
        if self._detalles.existe_por_medicamento(id_medicamento):
            raise MedicamentoConVentas(
                "No se puede eliminar: el medicamento figura en el detalle de ventas."
            )
        self._medicamentos.eliminar(id_medicamento)
