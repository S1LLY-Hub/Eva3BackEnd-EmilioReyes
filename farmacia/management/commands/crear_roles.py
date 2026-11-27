"""Crea los 2 roles (grupos) con permisos distintos y 1 usuario por rol.

    python manage.py crear_roles
    python manage.py crear_roles --password MiClaveSegura123

El superusuario se crea aparte:  python manage.py createsuperuser

No depende de la senal post_migrate: crea los permisos de los 5 modelos a mano,
porque las tablas son 'managed = False'."""
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from farmacia.infrastructure.models import (
    ClienteModel, DetalleVentaModel, LaboratorioModel, MedicamentoModel, VentaModel,
)

MODELOS = [LaboratorioModel, ClienteModel, MedicamentoModel, VentaModel, DetalleVentaModel]
ACCIONES = ("add", "change", "delete", "view")

# Administrador: todo. Vendedor: vende y atiende clientes, pero no toca el catalogo ni borra.
ROLES = {
    "Administrador": {m._meta.model_name: set(ACCIONES) for m in MODELOS},
    "Vendedor": {
        LaboratorioModel._meta.model_name: {"view"},
        MedicamentoModel._meta.model_name: {"view"},
        ClienteModel._meta.model_name: {"view", "add", "change"},
        VentaModel._meta.model_name: {"view", "add", "change"},
        DetalleVentaModel._meta.model_name: {"view", "add"},
    },
}

USUARIOS = {"admin_farmacia": "Administrador", "vendedor1": "Vendedor"}


def _permiso(modelo, accion):
    ct, _ = ContentType.objects.get_or_create(app_label="farmacia", model=modelo._meta.model_name)
    nombre = modelo._meta.model_name
    perm, _ = Permission.objects.get_or_create(
        content_type=ct, codename=f"{accion}_{nombre}",
        defaults={"name": f"Can {accion} {modelo._meta.verbose_name}"},
    )
    return perm


class Command(BaseCommand):
    help = "Crea los grupos Administrador y Vendedor y un usuario por cada uno."

    def add_arguments(self, parser):
        parser.add_argument("--password", default="Farmacia2026!",
                            help="Clave de los usuarios de prueba (cambiala).")

    def handle(self, *args, **opts):
        por_nombre = {m._meta.model_name: m for m in MODELOS}
        for rol, permisos in ROLES.items():
            grupo, _ = Group.objects.get_or_create(name=rol)
            grupo.permissions.set(
                [_permiso(por_nombre[n], a) for n, acciones in permisos.items() for a in acciones]
            )
            self.stdout.write(self.style.SUCCESS(f"Grupo '{rol}': {grupo.permissions.count()} permisos"))

        for username, rol in USUARIOS.items():
            user, creado = User.objects.get_or_create(
                username=username, defaults={"email": f"{username}@botica.cl", "is_staff": True})
            user.is_staff = True          # puede entrar al panel /admin/
            user.set_password(opts["password"])
            user.save()
            user.groups.set([Group.objects.get(name=rol)])
            self.stdout.write(self.style.SUCCESS(
                f"Usuario '{username}' ({'creado' if creado else 'actualizado'}) -> rol {rol}"))