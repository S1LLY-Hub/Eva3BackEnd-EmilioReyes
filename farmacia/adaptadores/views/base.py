from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from farmacia.adaptadores.permisos import PermisoPorModelo


class ListaCrearBase(APIView):
    """GET lista, POST crea. Las subclases definen: serializer_class, modelo_permiso, listar(), crear()."""
    permission_classes = [PermisoPorModelo]
    serializer_class = None
    modelo_permiso = None

    def get(self, request):
        return Response(self.serializer_class(self.listar(), many=True).data)

    def post(self, request):
        s = self.serializer_class(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(self.serializer_class(self.crear(s.validated_data)).data,
                        status=status.HTTP_201_CREATED)


class DetalleBase(APIView):
    """GET uno, PUT actualiza, DELETE borra. Subclases: obtener(), actualizar(), eliminar()."""
    permission_classes = [PermisoPorModelo]
    serializer_class = None
    modelo_permiso = None

    def get(self, request, pk):
        return Response(self.serializer_class(self.obtener(pk)).data)

    def put(self, request, pk):
        s = self.serializer_class(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(self.serializer_class(self.actualizar(pk, s.validated_data)).data)

    def delete(self, request, pk):
        self.eliminar(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)