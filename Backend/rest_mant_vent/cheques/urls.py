from django.urls import path, include

from .views import ventas_view, ventas_mantenido_view, folio_view, actualizar_venta, ventas_sin_impuesto

urlpatterns = [
    path('ventas', ventas_view, name='ventas'),
    path('aplicado', ventas_mantenido_view, name='ventas_mantenidas'),
    path('desglose/<str:folio>', folio_view, name='folio'),
    path('<str:folio>', actualizar_venta, name='mantenimiento_folio'),
    # Ventas sin impuesto
    path('tasa_cero/', ventas_sin_impuesto, name='ventas_sin_impuesto'),
]