# Django busca los modelos aqui. Los definimos en la capa de infraestructura
# y los reexportamos para que el registro de apps los encuentre.
from farmacia.infrastructure.models import *  # noqa: F401,F403
