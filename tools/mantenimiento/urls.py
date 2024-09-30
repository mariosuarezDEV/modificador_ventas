from django.urls import path
from .views import ver_cheques, ver_detalles, ver_pagos, mantenimiento_cuenta, cuentas_efectivo,cuentas_total_cero, cuentas_efectivo_facturadas

urlpatterns = [
    path('ventas/<str:folio>/', ver_cheques, name='ver_cheques'),
    path('detalles/<str:folio>/', ver_detalles, name='ver_detalles'),
    path('pagos/<str:folio>/', ver_pagos, name='ver_pagos'),
    path('actualizar/<str:folio>/', mantenimiento_cuenta, name='mantenimiento_cuenta'),
    
    # Filtrado de cheques
    path('cuentas/efectivo', cuentas_efectivo, name='cuentas_efectivo'),
    path('cuentas/efectivo/facturado', cuentas_efectivo_facturadas, name='cuentas_efectivo_facturadas'),
    path('cuentas/cero', cuentas_total_cero, name='cuentas_total_cero'),
]