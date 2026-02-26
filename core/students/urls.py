from django.urls import path
from .views import upload_students

urlpatterns = [
    path("upload/", upload_students),
]