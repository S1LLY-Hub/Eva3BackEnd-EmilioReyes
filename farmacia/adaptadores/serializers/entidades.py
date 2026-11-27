from rest_framework import serializers

from farmacia.domain.entities import EstadoVenta


class LaboratorioSerializer(serializers.Serializer):
    id_laboratorio = serializers.IntegerField(read_only=True)
    nombre = serializers.CharField(max_length=100)
    pais = serializers.CharField(max_length=60)


class ClienteSerializer(serializers.Serializer):
    id_cliente = serializers.IntegerField(read_only=True)
    rut = serializers.CharField(max_length=12)
    nombre = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    telefono = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True)
    fecha_registro = serializers.DateTimeField(read_only=True)


class MedicamentoSerializer(serializers.Serializer):
    id_medicamento = serializers.IntegerField(read_only=True)
    id_laboratorio = serializers.IntegerField()
    codigo = serializers.CharField(max_length=30)
    nombre = serializers.CharField(max_length=120)
    descripcion = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    precio = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.IntegerField(required=False, default=0)
    requiere_receta = serializers.BooleanField(required=False, default=False)
    fecha_vencimiento = serializers.DateField()


# ---- ventas ----
class LineaVentaSerializer(serializers.Serializer):
    id_medicamento = serializers.IntegerField()
    cantidad = serializers.IntegerField()


class VentaEntradaSerializer(serializers.Serializer):
    id_cliente = serializers.IntegerField()
    numero_receta = serializers.CharField(max_length=30, required=False, allow_null=True,
                                          allow_blank=True)
    detalles = LineaVentaSerializer(many=True)


class EstadoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=[e.value for e in EstadoVenta])


class DetalleVentaSalidaSerializer(serializers.Serializer):
    id_venta = serializers.IntegerField()
    id_medicamento = serializers.IntegerField()
    cantidad = serializers.IntegerField()
    precio_unitario = serializers.DecimalField(max_digits=10, decimal_places=2)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)


class VentaSalidaSerializer(serializers.Serializer):
    id_venta = serializers.IntegerField()
    id_cliente = serializers.IntegerField()
    fecha = serializers.DateTimeField()
    numero_receta = serializers.CharField(allow_null=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    estado = serializers.SerializerMethodField()

    def get_estado(self, venta):
        return venta.estado.value