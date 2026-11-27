"""Autenticacion por token guardado en una cookie HttpOnly.

- HttpOnly: JavaScript NO puede leer la cookie (document.cookie no la muestra),
  asi un ataque XSS no puede robar el token.
- Como el navegador envia la cookie AUTOMATICAMENTE, otro sitio podria forzar
  peticiones en nombre del usuario (CSRF). Por eso en POST/PUT/PATCH/DELETE
  exigimos ademas el header X-CSRFToken (que una pagina ajena no puede obtener)."""
from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import CSRFCheck, TokenAuthentication


class CookieTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get(settings.AUTH_COOKIE["NAME"])
        if not token:
            return None  # sin cookie: DRF prueba el siguiente autenticador (header Authorization)
        usuario, token_obj = self.authenticate_credentials(token)
        self._exigir_csrf(request)
        return usuario, token_obj

    def _exigir_csrf(self, request):
        check = CSRFCheck(lambda req: None)
        check.process_request(request)
        motivo = check.process_view(request, None, (), {})  # GET/HEAD/OPTIONS se saltan solos
        if motivo:
            raise exceptions.PermissionDenied(f"CSRF Failed: {motivo}")