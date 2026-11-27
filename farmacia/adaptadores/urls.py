from django.urls import path

from .views import auth, crud, ventas

urlpatterns = [
    # autenticacion
    path("auth/csrf/", auth.CsrfView.as_view()),
    path("auth/login/", auth.LoginView.as_view()),
    path("auth/logout/", auth.LogoutView.as_view()),
    path("auth/me/", auth.MeView.as_view()),
    # laboratorios, clientes, medicamentos
    path("laboratorios/", crud.LaboratoriosLista.as_view()),
    path("laboratorios/<int:pk>/", crud.LaboratorioDetalle.as_view()),
    path("clientes/", crud.ClientesLista.as_view()),
    path("clientes/<int:pk>/", crud.ClienteDetalle.as_view()),
    path("medicamentos/", crud.MedicamentosLista.as_view()),
    path("medicamentos/<int:pk>/", crud.MedicamentoDetalle.as_view()),
    # ventas (entidad principal)
    path("ventas/", ventas.VentasLista.as_view()),
    path("ventas/<int:pk>/", ventas.VentaDetalle.as_view()),
    path("ventas/<int:pk>/estado/", ventas.VentaCambiarEstado.as_view()),
]