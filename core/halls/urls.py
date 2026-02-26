from django.urls import path
from .views import create_hall

urlpatterns = [
    path("create/", create_hall),
]