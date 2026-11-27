"""Puerto de salida para ejecutar varias operaciones como UNA transaccion.
Python puro: la implementacion con Django vive en infrastructure."""
from abc import ABC, abstractmethod


class UnidadDeTrabajo(ABC):
    """Se usa con 'with': si dentro ocurre una excepcion, TODO se revierte."""

    @abstractmethod
    def __enter__(self): ...

    @abstractmethod
    def __exit__(self, exc_type, exc, tb): ...