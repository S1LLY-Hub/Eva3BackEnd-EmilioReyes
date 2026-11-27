"""Traduce las excepciones del dominio a respuestas HTTP (la API nunca devuelve 500 por reglas)."""
from rest_framework.response import Response
from rest_framework.views import exception_handler

from farmacia.domain.exceptions import (
    DatoInvalido, EliminacionProtegida, EntidadDuplicada, EntidadNoEncontrada, ErrorDeNegocio,
    MedicamentoVencido, RecetaRequerida, StockInsuficiente, TransicionInvalida,
)


def _estado_http(exc: ErrorDeNegocio) -> int:
    if isinstance(exc, EntidadNoEncontrada):
        return 404
    if isinstance(exc, (EntidadDuplicada, EliminacionProtegida, TransicionInvalida)):
        return 409
    if isinstance(exc, (MedicamentoVencido, StockInsuficiente, RecetaRequerida)):
        return 422  # reglas de negocio R1, R2, R3
    if isinstance(exc, DatoInvalido):
        return 400
    return 400


def manejador_errores(exc, context):
    if isinstance(exc, ErrorDeNegocio):
        return Response({"error": type(exc).__name__, "detalle": str(exc)},
                        status=_estado_http(exc))
    return exception_handler(exc, context)  # errores normales de DRF (401, 403, 400...)