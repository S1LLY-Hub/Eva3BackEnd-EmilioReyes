"""Pruebas de Venta: reglas R1, R2, R3, transiciones de estado y detalle.
Sin Django ni Oracle: usan los repositorios en memoria de farmacia/tests.py.
Ejecutar:  python -m unittest farmacia.tests_ventas -v"""
import unittest
from datetime import date
from decimal import Decimal

from farmacia.application.use_cases.laboratorios import CrearLaboratorio
from farmacia.application.use_cases.medicamentos import CrearMedicamento
from farmacia.application.use_cases.clientes import CrearCliente
from farmacia.application.use_cases.ventas import (
    CambiarEstadoVenta, CrearVenta, EliminarVenta, LineaVenta, ObtenerVenta,
)
from farmacia.domain.entities import EstadoVenta
from farmacia.domain.exceptions import (
    CantidadInvalida, EstadoDesconocido, MedicamentoVencido, RecetaRequerida,
    StockInsuficiente, TransicionInvalida, VentaNoEliminable, VentaSinDetalles,
)
from farmacia.domain.unidad_de_trabajo import UnidadDeTrabajo
from farmacia.tests import ClientesFake, DetallesFake, LabsFake, MedsFake, VentasFake

HOY = date(2026, 11, 26)


class UoWFalsa(UnidadDeTrabajo):
    def __enter__(self): return self
    def __exit__(self, *a): return False


class VentaBase(unittest.TestCase):
    def setUp(self):
        self.labs, self.meds, self.clientes = LabsFake(), MedsFake(), ClientesFake()
        self.ventas, self.detalles, self.uow = VentasFake(), DetallesFake(), UoWFalsa()
        lab = CrearLaboratorio(self.labs).ejecutar("Bayer", "Alemania")
        self.cliente = CrearCliente(self.clientes).ejecutar("1-9", "Ana")
        crear = CrearMedicamento(self.meds, self.labs).ejecutar
        self.libre = crear(lab.id_laboratorio, "MED-1", "Paracetamol", Decimal("1000"),
                           date(2027, 1, 1), stock=10)
        self.vencido = crear(lab.id_laboratorio, "MED-2", "Jarabe", Decimal("500"),
                             date(2026, 1, 1), stock=10)
        self.receta = crear(lab.id_laboratorio, "MED-3", "Amoxicilina", Decimal("6000"),
                            date(2027, 1, 1), stock=10, requiere_receta=True)
        self.crear = CrearVenta(self.ventas, self.detalles, self.meds, self.clientes,
                                self.uow, hoy=lambda: HOY)
        self.cambiar = CambiarEstadoVenta(self.ventas, self.detalles, self.meds, self.uow)

    def vender(self, med, cant, receta=None):
        return self.crear.ejecutar(self.cliente.id_cliente,
                                   [LineaVenta(med.id_medicamento, cant)], receta)


class ReglasTest(VentaBase):
    def test_venta_ok_calcula_total_y_descuenta_stock(self):
        r = self.crear.ejecutar(self.cliente.id_cliente, [
            LineaVenta(self.libre.id_medicamento, 2),
            LineaVenta(self.receta.id_medicamento, 1)], "REC-1")
        self.assertEqual(r.venta.total, Decimal("8000"))
        self.assertEqual(len(r.detalles), 2)
        self.assertEqual(self.meds.obtener(self.libre.id_medicamento).stock, 8)

    def test_R1_stock_insuficiente(self):
        with self.assertRaises(StockInsuficiente):
            self.vender(self.libre, 11)
        self.assertEqual(self.ventas.listar(), [])  # no quedo nada a medias

    def test_R2_medicamento_vencido(self):
        with self.assertRaises(MedicamentoVencido):
            self.vender(self.vencido, 1)
        self.assertEqual(self.meds.obtener(self.vencido.id_medicamento).stock, 10)

    def test_R3_receta_requerida(self):
        with self.assertRaises(RecetaRequerida):
            self.vender(self.receta, 1)
        self.vender(self.receta, 1, receta="REC-9")  # con receta si pasa

    def test_una_linea_mala_no_deja_venta_parcial(self):
        with self.assertRaises(MedicamentoVencido):
            self.crear.ejecutar(self.cliente.id_cliente, [
                LineaVenta(self.libre.id_medicamento, 1),
                LineaVenta(self.vencido.id_medicamento, 1)])
        self.assertEqual(self.ventas.listar(), [])
        self.assertEqual(self.meds.obtener(self.libre.id_medicamento).stock, 10)

    def test_sin_detalles_y_cantidad_invalida(self):
        with self.assertRaises(VentaSinDetalles):
            self.crear.ejecutar(self.cliente.id_cliente, [])
        with self.assertRaises(CantidadInvalida):
            self.vender(self.libre, 0)

    def test_lineas_repetidas_se_suman(self):
        r = self.crear.ejecutar(self.cliente.id_cliente, [
            LineaVenta(self.libre.id_medicamento, 2), LineaVenta(self.libre.id_medicamento, 3)])
        self.assertEqual(len(r.detalles), 1)
        self.assertEqual(r.detalles[0].cantidad, 5)


class EstadosTest(VentaBase):
    def test_flujo_valido_y_estado_final(self):
        v = self.vender(self.libre, 1).venta
        self.cambiar.ejecutar(v.id_venta, "pagada")
        self.cambiar.ejecutar(v.id_venta, "anulada")
        with self.assertRaises(TransicionInvalida):
            self.cambiar.ejecutar(v.id_venta, "pagada")  # anulada es final

    def test_pagada_no_vuelve_a_pendiente(self):
        v = self.vender(self.libre, 1).venta
        self.cambiar.ejecutar(v.id_venta, "pagada")
        with self.assertRaises(TransicionInvalida):
            self.cambiar.ejecutar(v.id_venta, "pendiente")

    def test_estado_desconocido(self):
        v = self.vender(self.libre, 1).venta
        with self.assertRaises(EstadoDesconocido):
            self.cambiar.ejecutar(v.id_venta, "regalada")

    def test_anular_devuelve_stock(self):
        v = self.vender(self.libre, 4).venta
        self.assertEqual(self.meds.obtener(self.libre.id_medicamento).stock, 6)
        self.cambiar.ejecutar(v.id_venta, "anulada")
        self.assertEqual(self.meds.obtener(self.libre.id_medicamento).stock, 10)

    def test_eliminar_pendiente_devuelve_stock_y_pagada_no_se_borra(self):
        eliminar = EliminarVenta(self.ventas, self.detalles, self.meds, self.uow)
        v1 = self.vender(self.libre, 3).venta
        eliminar.ejecutar(v1.id_venta)
        self.assertEqual(self.meds.obtener(self.libre.id_medicamento).stock, 10)
        self.assertEqual(self.detalles.items, [])
        v2 = self.vender(self.libre, 1).venta
        self.cambiar.ejecutar(v2.id_venta, "pagada")
        with self.assertRaises(VentaNoEliminable):
            eliminar.ejecutar(v2.id_venta)

    def test_obtener_trae_detalle(self):
        v = self.vender(self.libre, 2).venta
        r = ObtenerVenta(self.ventas, self.detalles).ejecutar(v.id_venta)
        self.assertEqual(r.venta.estado, EstadoVenta.PENDIENTE)
        self.assertEqual(r.detalles[0].subtotal, Decimal("2000"))


if __name__ == "__main__":
    unittest.main()