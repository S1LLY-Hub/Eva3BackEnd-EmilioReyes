from django.db import models

from .medicamento import MedicamentoModel
from .venta import VentaModel


class DetalleVentaModel(models.Model):
    # Clave compuesta (id_venta, id_medicamento): CompositePrimaryKey existe desde Django 5.2
    pk = models.CompositePrimaryKey("venta_id", "medicamento_id")
    venta = models.ForeignKey(
        VentaModel, on_delete=models.DO_NOTHING, db_column="id_venta", related_name="detalles",
    )
    medicamento = models.ForeignKey(
        MedicamentoModel, on_delete=models.DO_NOTHING, db_column="id_medicamento",
        related_name="detalles",
    )
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    # subtotal es columna VIRTUAL en Oracle: se declara como GeneratedField para que
    # Django nunca intente insertarla.
    subtotal = models.GeneratedField(
        expression=models.F("cantidad") * models.F("precio_unitario"),
        output_field=models.DecimalField(max_digits=12, decimal_places=2),
        db_persist=False,
    )

    class Meta:
        managed = False
        db_table = "detalle_venta"
        app_label = "farmacia"
