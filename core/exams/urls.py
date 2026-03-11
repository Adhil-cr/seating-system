from django.urls import path
from .views import create_exam, list_exams

urlpatterns = [
    path("create/", create_exam),
    path("list/", list_exams),
]
