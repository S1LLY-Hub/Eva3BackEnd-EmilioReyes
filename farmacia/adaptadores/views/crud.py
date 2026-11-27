"""CRUD de Laboratorio, Cliente y Medicamento. Cada metodo solo traduce HTTP <-> caso de uso."""
from farmacia.adaptadores import composicion as co
from farmacia.adaptadores.serializers import (
    ClienteSerializer, LaboratorioSerializer, MedicamentoSerializer,
)
from farmacia.infrastructure.models import ClienteModel, LaboratorioModel, MedicamentoModel

from .base import DetalleBase, ListaCrearBase


# ---------------- laboratorios ----------------
class LaboratoriosLista(ListaCrearBase):
    serializer_class = LaboratorioSerializer
    modelo_permiso = LaboratorioModel._meta.model_name

    def listar(self):
        return co.listar_laboratorios().ejecutar()

    def crear(self, d):
        return co.crear_laboratorio().ejecutar(d["nombre"], d["pais"])


class LaboratorioDetalle(DetalleBase):
    serializer_class = LaboratorioSerializer
    modelo_permiso = LaboratorioModel._meta.model_name

    def obtener(self, pk):
        return co.obtener_laboratorio().ejecutar(pk)

    def actualizar(self, pk, d):
        return co.actualizar_laboratorio().ejecutar(pk, d["nombre"], d["pais"])

    def eliminar(self, pk):
        co.eliminar_laboratorio().ejecutar(pk)


# ---------------- clientes ----------------
class ClientesLista(ListaCrearBase):
    serializer_class = ClienteSerializer
    modelo_permiso = ClienteModel._meta.model_name

    def listar(self):
        return co.listar_clientes().ejecutar()

    def crear(self, d):
        return co.crear_cliente().ejecutar(d["rut"], d["nombre"], d.get("email"), d.get("telefono"))


class ClienteDetalle(DetalleBase):
    serializer_class = ClienteSerializer
    modelo_permiso = ClienteModel._meta.model_name

    def obtener(self, pk):
        return co.obtener_cliente().ejecutar(pk)

    def actualizar(self, pk, d):
        return co.actualizar_cliente().ejecutar(
            pk, d["rut"], d["nombre"], d.get("email"), d.get("telefono"))

    def eliminar(self, pk):
        co.eliminar_cliente().ejecutar(pk)


# ---------------- medicamentos ----------------
class MedicamentosLista(ListaCrearBase):
    serializer_class = MedicamentoSerializer
    modelo_permiso = MedicamentoModel._meta.model_name

    def listar(self):
        return co.listar_medicamentos().ejecutar()

    def crear(self, d):
        return co.crear_medicamento().ejecutar(
            d["id_laboratorio"], d["codigo"], d["nombre"], d["precio"], d["fecha_vencimiento"],
            d.get("stock", 0), d.get("requiere_receta", False), d.get("descripcion"))


class MedicamentoDetalle(DetalleBase):
    serializer_class = MedicamentoSerializer
    modelo_permiso = MedicamentoModel._meta.model_name

    def obtener(self, pk):
        return co.obtener_medicamento().ejecutar(pk)

    def actualizar(self, pk, d):
        return co.actualizar_medicamento().ejecutar(
            pk, d["id_laboratorio"], d["codigo"], d["nombre"], d["precio"],
            d["fecha_vencimiento"], d.get("stock", 0), d.get("requiere_receta", False),
            d.get("descripcion"))

    def eliminar(self, pk):
        co.eliminar_medicamento().ejecutar(pk)