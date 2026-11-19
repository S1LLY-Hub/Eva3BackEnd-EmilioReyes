from django.db import models


class ClienteModel(models.Model):
    id_cliente = models.BigAutoField(primary_key=True, db_column="id_cliente")
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    fecha_registro = models.DateTimeField(null=True, blank=True)  # la pone Oracle (DEFAULT)

    class Meta:
        managed = False
        db_table = "clientes"
        app_label = "farmacia"
