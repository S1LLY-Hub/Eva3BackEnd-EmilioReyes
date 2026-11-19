"""Excepciones de negocio. Python puro: no dependen de Django ni de DRF.
La capa de adaptadores (views) las traduce a codigos HTTP."""


class ErrorDeNegocio(Exception):
    """Base de todas las excepciones del dominio."""


# ---- No encontrado (-> 404) ----
class EntidadNoEncontrada(ErrorDeNegocio):
    pass


class LaboratorioNoEncontrado(EntidadNoEncontrada):
    pass


class ClienteNoEncontrado(EntidadNoEncontrada):
    pass


class MedicamentoNoEncontrado(EntidadNoEncontrada):
    pass


# ---- Duplicados (-> 409) ----
class EntidadDuplicada(ErrorDeNegocio):
    pass


class LaboratorioDuplicado(EntidadDuplicada):
    """Ya existe un laboratorio con ese nombre (UNIQUE uq_laboratorios_nombre)."""


class ClienteDuplicado(EntidadDuplicada):
    """Ya existe un cliente con ese RUT o email (uq_clientes_rut / uq_clientes_email)."""


class MedicamentoDuplicado(EntidadDuplicada):
    """Ya existe un medicamento con ese codigo (uq_medicamentos_codigo)."""


# ---- Borrado protegido (-> 409) ----
class EliminacionProtegida(ErrorDeNegocio):
    pass


class LaboratorioConMedicamentos(EliminacionProtegida):
    """No se borra un laboratorio que tiene medicamentos asociados."""


class ClienteConVentas(EliminacionProtegida):
    """No se borra un cliente que tiene ventas registradas."""


class MedicamentoConVentas(EliminacionProtegida):
    """No se borra un medicamento que aparece en el detalle de alguna venta."""


# ---- Datos invalidos (-> 400) ----
class DatoInvalido(ErrorDeNegocio):
    pass


class PrecioInvalido(DatoInvalido):
    """precio < 0 (ck_medicamentos_precio)."""


class StockInvalido(DatoInvalido):
    """stock < 0 (ck_medicamentos_stock)."""


class CampoObligatorio(DatoInvalido):
    """Un campo NOT NULL llego vacio."""


# ---- Reglas de venta (se usaran en los casos de uso de ventas) ----
class MedicamentoVencido(ErrorDeNegocio):
    """R2: no se vende un medicamento con fecha_vencimiento pasada."""


class StockInsuficiente(ErrorDeNegocio):
    """La cantidad pedida supera el stock disponible."""


class RecetaRequerida(ErrorDeNegocio):
    """El medicamento exige receta y la venta no trae numero_receta."""
