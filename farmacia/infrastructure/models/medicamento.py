from django.db import models

from .laboratorio import LaboratorioModel


class MedicamentoModel(models.Model):
    id_medicamento = models.BigAutoField(primary_key=True, db_column="id_medicamento")
    laboratorio = models.ForeignKey(
        LaboratorioModel, on_delete=models.DO_NOTHING, db_column="id_laboratorio",
        related_name="medicamentos",
    )
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    requiere_receta = models.BooleanField(default=False)   # NUMBER(1) con CHECK 0/1
    fecha_vencimiento = models.DateField()

    class Meta:
        managed = False
        db_table = "medicamentos"
        app_label = "farmacia"
