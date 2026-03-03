from django.urls import path
from .views import preview_seating, generate_seating, view_seating

urlpatterns = [
    path("preview/", preview_seating),
    path("generate/", generate_seating),
    path("view/", view_seating),
]