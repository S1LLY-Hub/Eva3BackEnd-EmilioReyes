"""Punto unico donde se conectan los casos de uso con la infraestructura (ORM)."""
from farmacia.application.use_cases import clientes as c
from farmacia.application.use_cases import laboratorios as l
from farmacia.application.use_cases import medicamentos as m
from farmacia.application.use_cases import ventas as v
from farmacia.infrastructure.repositories import (
    ClienteRepositorioORM, DetalleVentaRepositorioORM, LaboratorioRepositorioORM,
    MedicamentoRepositorioORM, VentaRepositorioORM,
)
from farmacia.infrastructure.unidad_de_trabajo import UnidadDeTrabajoDjango


def _repos():
    return (LaboratorioRepositorioORM(), ClienteRepositorioORM(), MedicamentoRepositorioORM(),
            VentaRepositorioORM(), DetalleVentaRepositorioORM())


# ---- laboratorios ----
def crear_laboratorio():
    return l.CrearLaboratorio(_repos()[0])

def listar_laboratorios():
    return l.ListarLaboratorios(_repos()[0])

def obtener_laboratorio():
    return l.ObtenerLaboratorio(_repos()[0])

def actualizar_laboratorio():
    return l.ActualizarLaboratorio(_repos()[0])

def eliminar_laboratorio():
    labs, _, meds, _, _ = _repos()
    return l.EliminarLaboratorio(labs, meds)


# ---- clientes ----
def crear_cliente():
    return c.CrearCliente(_repos()[1])

def listar_clientes():
    return c.ListarClientes(_repos()[1])

def obtener_cliente():
    return c.ObtenerCliente(_repos()[1])

def actualizar_cliente():
    return c.ActualizarCliente(_repos()[1])

def eliminar_cliente():
    _, clientes, _, ventas, _ = _repos()
    return c.EliminarCliente(clientes, ventas)


# ---- medicamentos ----
def crear_medicamento():
    labs, _, meds, _, _ = _repos()
    return m.CrearMedicamento(meds, labs)

def listar_medicamentos():
    return m.ListarMedicamentos(_repos()[2])

def obtener_medicamento():
    return m.ObtenerMedicamento(_repos()[2])

def actualizar_medicamento():
    labs, _, meds, _, _ = _repos()
    return m.ActualizarMedicamento(meds, labs)

def eliminar_medicamento():
    _, _, meds, _, detalles = _repos()
    return m.EliminarMedicamento(meds, detalles)


# ---- ventas (con transaccion) ----
def crear_venta():
    _, clientes, meds, ventas, detalles = _repos()
    return v.CrearVenta(ventas, detalles, meds, clientes, UnidadDeTrabajoDjango())

def listar_ventas():
    return v.ListarVentas(_repos()[3])

def obtener_venta():
    _, _, _, ventas, detalles = _repos()
    return v.ObtenerVenta(ventas, detalles)

def cambiar_estado_venta():
    _, _, meds, ventas, detalles = _repos()
    return v.CambiarEstadoVenta(ventas, detalles, meds, UnidadDeTrabajoDjango())

def eliminar_venta():
    _, _, meds, ventas, detalles = _repos()
    return v.EliminarVenta(ventas, detalles, meds, UnidadDeTrabajoDjango())