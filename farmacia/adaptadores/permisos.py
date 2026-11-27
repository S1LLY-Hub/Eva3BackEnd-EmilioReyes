"""Autorizacion por rol: usa los permisos de Django asignados a cada grupo.
GET -> view | POST -> add | PUT/PATCH -> change | DELETE -> delete
Una vista puede fijar 'accion_permiso' para forzar la accion (ej. cambiar estado = change)."""
from rest_framework.permissions import BasePermission

ACCIONES = {
    "GET": "view", "HEAD": "view", "OPTIONS": "view",
    "POST": "add", "PUT": "change", "PATCH": "change", "DELETE": "delete",
}


class PermisoPorModelo(BasePermission):
    message = "Tu rol no tiene permiso para esta accion."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        accion = getattr(view, "accion_permiso", None) or ACCIONES.get(request.method)
        if accion is None:
            return False
        # superusuario: has_perm siempre devuelve True
        return user.has_perm(f"farmacia.{accion}_{view.modelo_permiso}")