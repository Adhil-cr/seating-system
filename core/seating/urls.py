from django.urls import path
from .views import preview_seating, generate_seating, view_seating
from .views import export_pdf

urlpatterns = [
    path("preview/", preview_seating),
    path("generate/", generate_seating),
    path("view/", view_seating),
    path("export/pdf/", export_pdf),
]



