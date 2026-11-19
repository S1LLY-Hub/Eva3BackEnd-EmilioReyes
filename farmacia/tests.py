"""Pruebas de la regla de dependencia y de los casos de uso.
Usan repositorios en memoria: NO necesitan Django, Oracle ni migraciones."""
import ast
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from farmacia.application.use_cases.clientes import (
    ActualizarCliente, CrearCliente, EliminarCliente,
)
from farmacia.application.use_cases.laboratorios import (
    ActualizarLaboratorio, CrearLaboratorio, EliminarLaboratorio,
)
from farmacia.application.use_cases.medicamentos import (
    CrearMedicamento, EliminarMedicamento,
)
from farmacia.domain.entities import Cliente, DetalleVenta, Laboratorio, Medicamento, Venta
from farmacia.domain.exceptions import (
    ClienteConVentas, ClienteDuplicado, LaboratorioConMedicamentos, LaboratorioDuplicado,
    LaboratorioNoEncontrado, MedicamentoConVentas, MedicamentoDuplicado, PrecioInvalido,
)
from farmacia.domain.repositories import (
    ClienteRepositorio, DetalleVentaRepositorio, LaboratorioRepositorio,
    MedicamentoRepositorio, VentaRepositorio,
)


# ---------------- repositorios falsos (implementan los puertos) ----------------
class _Memoria:
    def __init__(self, id_attr):
        self.datos, self._sig, self._id = {}, 1, id_attr

    def listar(self):
        return list(self.datos.values())

    def obtener(self, id_):
        return self.datos.get(id_)

    def guardar(self, e):
        if getattr(e, self._id) is None:
            setattr(e, self._id, self._sig)
            self._sig += 1
        self.datos[getattr(e, self._id)] = e
        return e

    def eliminar(self, id_):
        self.datos.pop(id_, None)


class LabsFake(_Memoria, LaboratorioRepositorio):
    def __init__(self): super().__init__("id_laboratorio")
    def obtener_por_nombre(self, n): return next((x for x in self.datos.values() if x.nombre.lower() == n.lower()), None)


class ClientesFake(_Memoria, ClienteRepositorio):
    def __init__(self): super().__init__("id_cliente")
    def obtener_por_rut(self, r): return next((x for x in self.datos.values() if x.rut == r), None)
    def obtener_por_email(self, e): return next((x for x in self.datos.values() if x.email and x.email.lower() == e.lower()), None)


class MedsFake(_Memoria, MedicamentoRepositorio):
    def __init__(self): super().__init__("id_medicamento")
    def obtener_por_codigo(self, c): return next((x for x in self.datos.values() if x.codigo == c), None)
    def existe_por_laboratorio(self, i): return any(x.id_laboratorio == i for x in self.datos.values())


class VentasFake(_Memoria, VentaRepositorio):
    def __init__(self): super().__init__("id_venta")
    def existe_por_cliente(self, i): return any(x.id_cliente == i for x in self.datos.values())


class DetallesFake(DetalleVentaRepositorio):
    def __init__(self): self.items = []
    def listar_por_venta(self, i): return [d for d in self.items if d.id_venta == i]
    def existe_por_medicamento(self, i): return any(d.id_medicamento == i for d in self.items)
    def guardar(self, d): self.items.append(d); return d
    def eliminar(self, v, m): self.items = [d for d in self.items if (d.id_venta, d.id_medicamento) != (v, m)]


# ---------------- regla de dependencia ----------------
class ReglaDeDependenciaTest(unittest.TestCase):
    """domain y application no pueden importar django, rest_framework ni infrastructure."""
    PROHIBIDOS = ("django", "rest_framework", "farmacia.infrastructure", "farmacia.adaptadores")

    def _importaciones(self, carpeta):
        base = Path(__file__).parent / carpeta
        for archivo in base.rglob("*.py"):
            for nodo in ast.walk(ast.parse(archivo.read_text(encoding="utf-8"))):
                if isinstance(nodo, ast.Import):
                    for a in nodo.names:
                        yield archivo, a.name
                elif isinstance(nodo, ast.ImportFrom) and nodo.module:
                    yield archivo, nodo.module

    def test_dominio_y_aplicacion_no_importan_capas_externas(self):
        for carpeta in ("domain", "application"):
            for archivo, modulo in self._importaciones(carpeta):
                self.assertFalse(modulo.startswith(self.PROHIBIDOS),
                                 f"{archivo.name} importa '{modulo}' (viola la regla de dependencia)")


# ---------------- casos de uso ----------------
class LaboratorioTest(unittest.TestCase):
    def setUp(self):
        self.labs, self.meds = LabsFake(), MedsFake()

    def test_crear_y_rechazar_duplicado(self):
        CrearLaboratorio(self.labs).ejecutar("Bayer", "Alemania")
        with self.assertRaises(LaboratorioDuplicado):
            CrearLaboratorio(self.labs).ejecutar("bayer", "Alemania")

    def test_actualizar_a_nombre_de_otro_es_duplicado(self):
        CrearLaboratorio(self.labs).ejecutar("Bayer", "Alemania")
        b = CrearLaboratorio(self.labs).ejecutar("Saval", "Chile")
        with self.assertRaises(LaboratorioDuplicado):
            ActualizarLaboratorio(self.labs).ejecutar(b.id_laboratorio, "Bayer", "Chile")
        # conservar su propio nombre NO es duplicado
        ActualizarLaboratorio(self.labs).ejecutar(b.id_laboratorio, "Saval", "Peru")

    def test_borrado_protegido(self):
        lab = CrearLaboratorio(self.labs).ejecutar("Bayer", "Alemania")
        CrearMedicamento(self.meds, self.labs).ejecutar(
            lab.id_laboratorio, "MED-1", "Aspirina", Decimal("1000"), date(2030, 1, 1))
        with self.assertRaises(LaboratorioConMedicamentos):
            EliminarLaboratorio(self.labs, self.meds).ejecutar(lab.id_laboratorio)
        self.meds.datos.clear()
        EliminarLaboratorio(self.labs, self.meds).ejecutar(lab.id_laboratorio)
        self.assertIsNone(self.labs.obtener(lab.id_laboratorio))


class ClienteTest(unittest.TestCase):
    def setUp(self):
        self.clientes, self.ventas = ClientesFake(), VentasFake()

    def test_duplicado_por_rut_y_por_email(self):
        CrearCliente(self.clientes).ejecutar("1-9", "Ana", "ana@x.cl")
        with self.assertRaises(ClienteDuplicado):
            CrearCliente(self.clientes).ejecutar("1-9", "Otra")
        with self.assertRaises(ClienteDuplicado):
            CrearCliente(self.clientes).ejecutar("2-7", "Otra", "ANA@x.cl")

    def test_actualizar_con_rut_ajeno_falla(self):
        CrearCliente(self.clientes).ejecutar("1-9", "Ana")
        b = CrearCliente(self.clientes).ejecutar("2-7", "Beto")
        with self.assertRaises(ClienteDuplicado):
            ActualizarCliente(self.clientes).ejecutar(b.id_cliente, "1-9", "Beto")

    def test_borrado_protegido(self):
        c = CrearCliente(self.clientes).ejecutar("1-9", "Ana")
        self.ventas.guardar(Venta(id_cliente=c.id_cliente))
        with self.assertRaises(ClienteConVentas):
            EliminarCliente(self.clientes, self.ventas).ejecutar(c.id_cliente)


class MedicamentoTest(unittest.TestCase):
    def setUp(self):
        self.labs, self.meds, self.detalles = LabsFake(), MedsFake(), DetallesFake()
        self.lab = CrearLaboratorio(self.labs).ejecutar("Bayer", "Alemania")

    def _crear(self, codigo="MED-1", precio="1000"):
        return CrearMedicamento(self.meds, self.labs).ejecutar(
            self.lab.id_laboratorio, codigo, "Aspirina", Decimal(precio), date(2030, 1, 1))

    def test_codigo_duplicado(self):
        self._crear()
        with self.assertRaises(MedicamentoDuplicado):
            self._crear()

    def test_precio_negativo(self):
        with self.assertRaises(PrecioInvalido):
            self._crear(precio="-1")

    def test_laboratorio_inexistente(self):
        with self.assertRaises(LaboratorioNoEncontrado):
            CrearMedicamento(self.meds, self.labs).ejecutar(
                999, "MED-9", "X", Decimal("1"), date(2030, 1, 1))

    def test_borrado_protegido(self):
        m = self._crear()
        self.detalles.guardar(DetalleVenta(1, m.id_medicamento, 2, Decimal("1000")))
        with self.assertRaises(MedicamentoConVentas):
            EliminarMedicamento(self.meds, self.detalles).ejecutar(m.id_medicamento)

    def test_entidad_vencido_y_subtotal(self):
        m = Medicamento(1, "X", "X", Decimal("1"), date(2020, 1, 1))
        self.assertTrue(m.esta_vencido(date(2026, 11, 19)))
        self.assertEqual(DetalleVenta(1, 1, 3, Decimal("1500")).subtotal, Decimal("4500"))


if __name__ == "__main__":
    unittest.main()
