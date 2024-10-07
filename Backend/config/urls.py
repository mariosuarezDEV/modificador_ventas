from django.urls import path

from .views import obtener_ventas, actualizar_venta

urlpatterns = [
    path("ventas", obtener_ventas, name="ventas"),
    path("mantenimiento/<str:folio>", actualizar_venta, name="actualizar_venta"),
]
