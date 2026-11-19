from django.db import models


class LaboratorioModel(models.Model):
    id_laboratorio = models.BigAutoField(primary_key=True, db_column="id_laboratorio")
    nombre = models.CharField(max_length=100, unique=True)
    pais = models.CharField(max_length=60)

    class Meta:
        managed = False          # la tabla ya existe en Oracle (sql/01_crear_tablas.sql)
        db_table = "laboratorios"
        app_label = "farmacia"
