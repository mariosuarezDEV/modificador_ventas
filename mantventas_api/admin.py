from django.contrib import admin

# Register your models here.
from .models import Cheques, Cheqdet, Productos, Chequespagos, Productosdetalle

class ChequesAdmin(admin.ModelAdmin):
    # Presentacion de datos
    list_display = ['folio', 'efectivo', 'tarjeta', 'mesa', 'total', 'facturado']

class CheqdetAdmin(admin.ModelAdmin):
    list_display = ['foliodet', 'movimiento', 'precio', 'preciosinimpuestos', 'impuesto1']

admin.site.register(Cheques, ChequesAdmin)
admin.site.register(Cheqdet, CheqdetAdmin)
admin.site.register(Productos)
admin.site.register(Chequespagos)
admin.site.register(Productosdetalle)