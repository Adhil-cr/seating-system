from django.urls import path
from .views import create_exam

urlpatterns = [
    path("create/", create_exam),
]