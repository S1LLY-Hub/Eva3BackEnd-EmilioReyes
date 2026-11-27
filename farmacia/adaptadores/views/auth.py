"""Login, logout y /api/auth/me/ con cookie HttpOnly + CSRF."""
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

COOKIE = settings.AUTH_COOKIE


def _datos_usuario(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_superuser": user.is_superuser,
        "roles": list(user.groups.values_list("name", flat=True)),
    }


class CsrfView(APIView):
    """GET /api/auth/csrf/ -> el navegador recibe la cookie 'csrftoken' (legible por JS)."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({"detalle": "Cookie CSRF establecida."})


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


@method_decorator(csrf_protect, name="dispatch")  # el login tambien exige X-CSRFToken
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = authenticate(request, username=s.validated_data["username"],
                            password=s.validated_data["password"])
        if user is None:
            return Response({"detalle": "Credenciales invalidas."},
                            status=status.HTTP_401_UNAUTHORIZED)
        Token.objects.filter(user=user).delete()   # un token nuevo por cada login
        token = Token.objects.create(user=user)
        resp = Response(_datos_usuario(user))      # el token NO viaja en el cuerpo
        resp.set_cookie(
            COOKIE["NAME"], token.key, max_age=COOKIE["MAX_AGE"], path=COOKIE["PATH"],
            httponly=True, secure=COOKIE["SECURE"], samesite=COOKIE["SAMESITE"],
        )
        return resp


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # CookieTokenAuthentication ya exigio CSRF

    def post(self, request):
        Token.objects.filter(user=request.user).delete()  # el token deja de servir en el servidor
        resp = Response({"detalle": "Sesion cerrada."})
        resp.delete_cookie(COOKIE["NAME"], path=COOKIE["PATH"], samesite=COOKIE["SAMESITE"])
        return resp


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_datos_usuario(request.user))