"""Casos de uso CRUD de Laboratorio.
Solo importan dominio (entidades, excepciones, puertos). Nada de Django."""
from typing import List

from farmacia.domain.entities import Laboratorio
from farmacia.domain.exceptions import (
    CampoObligatorio,
    LaboratorioConMedicamentos,
    LaboratorioDuplicado,
    LaboratorioNoEncontrado,
)
from farmacia.domain.repositories import LaboratorioRepositorio, MedicamentoRepositorio


def _validar(nombre: str, pais: str) -> None:
    if not nombre or not nombre.strip():
        raise CampoObligatorio("El nombre del laboratorio es obligatorio.")
    if not pais or not pais.strip():
        raise CampoObligatorio("El pais del laboratorio es obligatorio.")


class CrearLaboratorio:
    def __init__(self, laboratorios: LaboratorioRepositorio):
        self._laboratorios = laboratorios

    def ejecutar(self, nombre: str, pais: str) -> Laboratorio:
        _validar(nombre, pais)
        if self._laboratorios.obtener_por_nombre(nombre.strip()):
            raise LaboratorioDuplicado(f"Ya existe el laboratorio '{nombre}'.")
        return self._laboratorios.guardar(Laboratorio(nombre=nombre.strip(), pais=pais.strip()))


class ListarLaboratorios:
    def __init__(self, laboratorios: LaboratorioRepositorio):
        self._laboratorios = laboratorios

    def ejecutar(self) -> List[Laboratorio]:
        return self._laboratorios.listar()


class ObtenerLaboratorio:
    def __init__(self, laboratorios: LaboratorioRepositorio):
        self._laboratorios = laboratorios

    def ejecutar(self, id_laboratorio: int) -> Laboratorio:
        lab = self._laboratorios.obtener(id_laboratorio)
        if lab is None:
            raise LaboratorioNoEncontrado(f"No existe el laboratorio {id_laboratorio}.")
        return lab


class ActualizarLaboratorio:
    def __init__(self, laboratorios: LaboratorioRepositorio):
        self._laboratorios = laboratorios

    def ejecutar(self, id_laboratorio: int, nombre: str, pais: str) -> Laboratorio:
        _validar(nombre, pais)
        lab = self._laboratorios.obtener(id_laboratorio)
        if lab is None:
            raise LaboratorioNoEncontrado(f"No existe el laboratorio {id_laboratorio}.")
        otro = self._laboratorios.obtener_por_nombre(nombre.strip())
        if otro is not None and otro.id_laboratorio != id_laboratorio:
            raise LaboratorioDuplicado(f"Ya existe el laboratorio '{nombre}'.")
        lab.nombre, lab.pais = nombre.strip(), pais.strip()
        return self._laboratorios.guardar(lab)


class EliminarLaboratorio:
    """Borrado protegido: no se elimina si tiene medicamentos."""

    def __init__(self, laboratorios: LaboratorioRepositorio, medicamentos: MedicamentoRepositorio):
        self._laboratorios = laboratorios
        self._medicamentos = medicamentos

    def ejecutar(self, id_laboratorio: int) -> None:
        if self._laboratorios.obtener(id_laboratorio) is None:
            raise LaboratorioNoEncontrado(f"No existe el laboratorio {id_laboratorio}.")
        if self._medicamentos.existe_por_laboratorio(id_laboratorio):
            raise LaboratorioConMedicamentos(
                "No se puede eliminar: el laboratorio tiene medicamentos asociados."
            )
        self._laboratorios.eliminar(id_laboratorio)
