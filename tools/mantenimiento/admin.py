from django.contrib import admin

# Register your models here.
from .models import Cheques, Cheqdet, Chequespagos

admin.site.register(Cheques)
admin.site.register(Cheqdet)
admin.site.register(Chequespagos)