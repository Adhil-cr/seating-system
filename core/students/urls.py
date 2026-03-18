from django.urls import path
from .views import upload_students, upload_history

urlpatterns = [
    path("upload/", upload_students),
    path("upload-history/", upload_history),
]
