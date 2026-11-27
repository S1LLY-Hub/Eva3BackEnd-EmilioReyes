from datetime import date

from django.contrib import admin

from farmacia.infrastructure.models import (
    ClienteModel, DetalleVentaModel, LaboratorioModel, MedicamentoModel, VentaModel,
)

admin.site.site_header = "Botica Central - Administracion"
admin.site.site_title = "Botica Central"


@admin.register(LaboratorioModel)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ("id_laboratorio", "nombre", "pais")
    search_fields = ("nombre", "pais")
    list_filter = ("pais",)
    ordering = ("nombre",)


@admin.register(ClienteModel)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("id_cliente", "rut", "nombre", "email", "telefono", "fecha_registro")
    search_fields = ("rut", "nombre", "email")
    list_filter = ("fecha_registro",)
    readonly_fields = ("fecha_registro",)
    ordering = ("nombre",)


@admin.register(MedicamentoModel)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "laboratorio", "precio", "stock",
                    "requiere_receta", "fecha_vencimiento", "vencido")
    search_fields = ("codigo", "nombre", "laboratorio__nombre")
    list_filter = ("requiere_receta", "laboratorio", "fecha_vencimiento")
    ordering = ("codigo",)

    @admin.display(boolean=True, description="Vencido")
    def vencido(self, obj):
        return obj.fecha_vencimiento < date.today()


@admin.register(VentaModel)
class VentaAdmin(admin.ModelAdmin):
    """Solo consulta: las ventas se crean y cambian por la API para que se cumplan R1, R2, R3
    y las transiciones de estado."""
    list_display = ("id_venta", "cliente", "fecha", "estado", "total", "numero_receta")
    search_fields = ("id_venta", "cliente__nombre", "cliente__rut", "numero_receta")
    list_filter = ("estado", "fecha")
    ordering = ("-id_venta",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DetalleVentaModel)
class DetalleVentaAdmin(admin.ModelAdmin):
    """Solo consulta. La PK es compuesta (id_venta, id_medicamento): sin enlaces de edicion."""
    list_display = ("venta", "medicamento", "cantidad", "precio_unitario", "subtotal")
    list_display_links = None
    search_fields = ("medicamento__codigo", "medicamento__nombre", "venta__cliente__nombre")
    list_filter = ("medicamento",)
    ordering = ("venta", "medicamento")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False