from django.urls import path, include

from .views import nexi_bot

urlpatterns = [
    path('', nexi_bot, name='nexi_bot'),
]