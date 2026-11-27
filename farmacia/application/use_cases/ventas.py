"""Casos de uso de Venta (entidad principal) con su detalle en UNA transaccion.

Reglas de negocio:
  R1  stock suficiente      -> StockInsuficiente
  R2  no vender vencidos    -> MedicamentoVencido
  R3  receta si la exige    -> RecetaRequerida
Estados: pendiente -> pagada -> anulada (ver TRANSICIONES_VALIDAS).
Solo dependen del dominio."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Callable, Dict, List, Optional

from farmacia.domain.entities import DetalleVenta, EstadoVenta, Venta
from farmacia.domain.exceptions import (
    CantidadInvalida,
    ClienteNoEncontrado,
    EstadoDesconocido,
    MedicamentoNoEncontrado,
    MedicamentoVencido,
    RecetaRequerida,
    StockInsuficiente,
    TransicionInvalida,
    VentaNoEliminable,
    VentaNoEncontrada,
    VentaSinDetalles,
)
from farmacia.domain.repositories import (
    ClienteRepositorio,
    DetalleVentaRepositorio,
    MedicamentoRepositorio,
    VentaRepositorio,
)
from farmacia.domain.unidad_de_trabajo import UnidadDeTrabajo


@dataclass
class LineaVenta:
    id_medicamento: int
    cantidad: int


@dataclass
class VentaConDetalle:
    venta: Venta
    detalles: List[DetalleVenta]


def _agrupar(lineas: List[LineaVenta]) -> List[LineaVenta]:
    """Valida y suma lineas repetidas del mismo medicamento (la PK del detalle es compuesta)."""
    if not lineas:
        raise VentaSinDetalles("La venta necesita al menos un medicamento.")
    acumulado: Dict[int, int] = {}
    for linea in lineas:
        if linea.cantidad is None or linea.cantidad <= 0:
            raise CantidadInvalida("La cantidad debe ser mayor que cero.")
        acumulado[linea.id_medicamento] = acumulado.get(linea.id_medicamento, 0) + linea.cantidad
    return [LineaVenta(i, c) for i, c in acumulado.items()]


class CrearVenta:
    def __init__(self, ventas: VentaRepositorio, detalles: DetalleVentaRepositorio,
                 medicamentos: MedicamentoRepositorio, clientes: ClienteRepositorio,
                 uow: UnidadDeTrabajo, hoy: Callable[[], date] = date.today):
        self._ventas, self._detalles = ventas, detalles
        self._medicamentos, self._clientes = medicamentos, clientes
        self._uow, self._hoy = uow, hoy

    def ejecutar(self, id_cliente: int, lineas: List[LineaVenta],
                 numero_receta: Optional[str] = None) -> VentaConDetalle:
        lineas = _agrupar(lineas)
        numero_receta = (numero_receta or "").strip() or None
        if self._clientes.obtener(id_cliente) is None:
            raise ClienteNoEncontrado(f"No existe el cliente {id_cliente}.")

        with self._uow:  # <- todo lo de abajo es UNA transaccion
            # 1) validar TODAS las lineas antes de escribir nada
            a_vender = []
            for linea in lineas:
                med = self._medicamentos.obtener(linea.id_medicamento)
                if med is None:
                    raise MedicamentoNoEncontrado(f"No existe el medicamento {linea.id_medicamento}.")
                if med.esta_vencido(self._hoy()):                       # R2
                    raise MedicamentoVencido(f"{med.codigo} esta vencido y no se puede vender.")
                if med.stock < linea.cantidad:                          # R1
                    raise StockInsuficiente(
                        f"{med.codigo}: stock {med.stock}, se pidieron {linea.cantidad}.")
                if med.requiere_receta and not numero_receta:           # R3
                    raise RecetaRequerida(f"{med.codigo} exige receta: falta numero_receta.")
                a_vender.append((med, linea.cantidad))

            # 2) escribir: cabecera, detalle, descuento de stock y total
            venta = self._ventas.guardar(Venta(id_cliente=id_cliente, numero_receta=numero_receta))
            detalles, total = [], Decimal("0")
            for med, cantidad in a_vender:
                detalle = self._detalles.guardar(DetalleVenta(
                    id_venta=venta.id_venta, id_medicamento=med.id_medicamento,
                    cantidad=cantidad, precio_unitario=med.precio))
                med.stock -= cantidad
                self._medicamentos.guardar(med)
                detalles.append(detalle)
                total += detalle.subtotal
            venta.total = total
            venta = self._ventas.guardar(venta)
        return VentaConDetalle(venta, detalles)


class ListarVentas:
    def __init__(self, ventas: VentaRepositorio):
        self._ventas = ventas

    def ejecutar(self) -> List[Venta]:
        return self._ventas.listar()


class ObtenerVenta:
    """Devuelve la venta CON su detalle."""

    def __init__(self, ventas: VentaRepositorio, detalles: DetalleVentaRepositorio):
        self._ventas, self._detalles = ventas, detalles

    def ejecutar(self, id_venta: int) -> VentaConDetalle:
        venta = self._ventas.obtener(id_venta)
        if venta is None:
            raise VentaNoEncontrada(f"No existe la venta {id_venta}.")
        return VentaConDetalle(venta, self._detalles.listar_por_venta(id_venta))


def _devolver_stock(detalles: List[DetalleVenta], medicamentos: MedicamentoRepositorio) -> None:
    for d in detalles:
        med = medicamentos.obtener(d.id_medicamento)
        if med is not None:
            med.stock += d.cantidad
            medicamentos.guardar(med)


class CambiarEstadoVenta:
    """Aplica la maquina de estados. Al ANULAR devuelve el stock (misma transaccion)."""

    def __init__(self, ventas: VentaRepositorio, detalles: DetalleVentaRepositorio,
                 medicamentos: MedicamentoRepositorio, uow: UnidadDeTrabajo):
        self._ventas, self._detalles = ventas, detalles
        self._medicamentos, self._uow = medicamentos, uow

    def ejecutar(self, id_venta: int, nuevo_estado: str) -> VentaConDetalle:
        try:
            nuevo = EstadoVenta(nuevo_estado)
        except ValueError:
            raise EstadoDesconocido(f"Estado desconocido: '{nuevo_estado}'.")
        venta = self._ventas.obtener(id_venta)
        if venta is None:
            raise VentaNoEncontrada(f"No existe la venta {id_venta}.")
        if not venta.puede_pasar_a(nuevo):
            raise TransicionInvalida(
                f"No se puede pasar de '{venta.estado.value}' a '{nuevo.value}'.")
        detalles = self._detalles.listar_por_venta(id_venta)
        with self._uow:
            if nuevo is EstadoVenta.ANULADA:
                _devolver_stock(detalles, self._medicamentos)
            venta.estado = nuevo
            venta = self._ventas.guardar(venta)
        return VentaConDetalle(venta, detalles)


class EliminarVenta:
    """Solo se borra una venta pendiente o anulada. Una PAGADA primero se anula."""

    def __init__(self, ventas: VentaRepositorio, detalles: DetalleVentaRepositorio,
                 medicamentos: MedicamentoRepositorio, uow: UnidadDeTrabajo):
        self._ventas, self._detalles = ventas, detalles
        self._medicamentos, self._uow = medicamentos, uow

    def ejecutar(self, id_venta: int) -> None:
        venta = self._ventas.obtener(id_venta)
        if venta is None:
            raise VentaNoEncontrada(f"No existe la venta {id_venta}.")
        if venta.estado is EstadoVenta.PAGADA:
            raise VentaNoEliminable("No se puede eliminar una venta pagada: primero anulela.")
        detalles = self._detalles.listar_por_venta(id_venta)
        with self._uow:
            if venta.estado is EstadoVenta.PENDIENTE:  # la anulada ya devolvio su stock
                _devolver_stock(detalles, self._medicamentos)
            for d in detalles:
                self._detalles.eliminar(d.id_venta, d.id_medicamento)
            self._ventas.eliminar(id_venta)