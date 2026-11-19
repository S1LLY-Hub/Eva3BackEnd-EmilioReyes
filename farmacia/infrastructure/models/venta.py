from django.db import models

from .cliente import ClienteModel


class VentaModel(models.Model):
    id_venta = models.BigAutoField(primary_key=True, db_column="id_venta")
    cliente = models.ForeignKey(
        ClienteModel, on_delete=models.DO_NOTHING, db_column="id_cliente",
        related_name="ventas",
    )
    fecha = models.DateTimeField(null=True, blank=True)       # DEFAULT en Oracle
    numero_receta = models.CharField(max_length=30, null=True, blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=9, default="pendiente")

    class Meta:
        managed = False
        db_table = "ventas"
        app_label = "farmacia"
