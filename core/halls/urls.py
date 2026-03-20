from django.urls import path
from .views import create_hall, list_halls, delete_hall

urlpatterns = [
    path("list/", list_halls),
    path("create/", create_hall),
    path("delete/<int:hall_id>/", delete_hall),
]
