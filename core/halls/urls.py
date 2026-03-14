from django.urls import path
from .views import create_hall, list_halls

urlpatterns = [
    path("list/", list_halls),
    path("create/", create_hall),
]
