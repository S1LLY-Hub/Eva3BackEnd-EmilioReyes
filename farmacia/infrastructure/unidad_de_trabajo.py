"""Adaptador del puerto UnidadDeTrabajo: una transaccion en la base Oracle ("negocio")."""
from django.db import transaction

from farmacia.domain.unidad_de_trabajo import UnidadDeTrabajo


class UnidadDeTrabajoDjango(UnidadDeTrabajo):
    def __enter__(self):
        self._atomic = transaction.atomic(using="negocio")
        self._atomic.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        # Si hubo excepcion, atomic hace ROLLBACK y la excepcion sigue su camino.
        return self._atomic.__exit__(exc_type, exc, tb)