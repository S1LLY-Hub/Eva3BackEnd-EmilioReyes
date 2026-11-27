"""Ventas: la entidad principal, con su detalle en una transaccion."""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from farmacia.adaptadores import composicion as co
from farmacia.adaptadores.permisos import PermisoPorModelo
from farmacia.adaptadores.serializers import (
    DetalleVentaSalidaSerializer, EstadoSerializer, VentaEntradaSerializer, VentaSalidaSerializer,
)
from farmacia.application.use_cases.ventas import LineaVenta
from farmacia.infrastructure.models import VentaModel


def _venta_con_detalle(resultado):
    data = VentaSalidaSerializer(resultado.venta).data
    data["detalles"] = DetalleVentaSalidaSerializer(resultado.detalles, many=True).data
    return data


class VentasLista(APIView):
    permission_classes = [PermisoPorModelo]
    modelo_permiso = VentaModel._meta.model_name

    def get(self, request):
        return Response(VentaSalidaSerializer(co.listar_ventas().ejecutar(), many=True).data)

    def post(self, request):
        s = VentaEntradaSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        lineas = [LineaVenta(x["id_medicamento"], x["cantidad"]) for x in d["detalles"]]
        resultado = co.crear_venta().ejecutar(d["id_cliente"], lineas, d.get("numero_receta"))
        return Response(_venta_con_detalle(resultado), status=status.HTTP_201_CREATED)


class VentaDetalle(APIView):
    permission_classes = [PermisoPorModelo]
    modelo_permiso = VentaModel._meta.model_name

    def get(self, request, pk):
        return Response(_venta_con_detalle(co.obtener_venta().ejecutar(pk)))

    def delete(self, request, pk):
        co.eliminar_venta().ejecutar(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class VentaCambiarEstado(APIView):
    """POST /api/ventas/<id>/estado/  {"estado": "pagada"}"""
    permission_classes = [PermisoPorModelo]
    modelo_permiso = VentaModel._meta.model_name
    accion_permiso = "change"   # es un POST, pero modifica una venta existente

    def post(self, request, pk):
        s = EstadoSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        resultado = co.cambiar_estado_venta().ejecutar(pk, s.validated_data["estado"])
        return Response(_venta_con_detalle(resultado))