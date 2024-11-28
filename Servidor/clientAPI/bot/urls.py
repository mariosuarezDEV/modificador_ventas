from django.urls import path

from .views import nexium_bot

urlpatterns = [
    path("", nexium_bot, name="home_bot"),
]
