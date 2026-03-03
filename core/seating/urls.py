from django.urls import path
from .views import preview_seating, generate_seating

urlpatterns = [
    path("preview/", preview_seating),
    path("generate/", generate_seating),
]