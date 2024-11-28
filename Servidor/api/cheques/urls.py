from django.urls import path, include

from .views import (
    ventas_view,
    ventas_mantenido_view,
    folio_view,
    actualizar_venta,
    ventas_sin_impuesto,
)

urlpatterns = [
    path("ventas", ventas_view, name="ventas"),  # Obtener todas las ventas
    path(
        "aplicado", ventas_mantenido_view, name="ventas_mantenidas"
    ),  # Obtener ventas con mantenimiento
    path(
        "desglose/<str:folio>", folio_view, name="folio"
    ),  # Ver informacion de un folio
    path(
        "<str:folio>", actualizar_venta, name="mantenimiento_folio"
    ),  # Mantenimiento de un folio
    path(
        "tasa_cero/", ventas_sin_impuesto, name="ventas_sin_impuesto"
    ),  # Ventas sin impuesto
]
