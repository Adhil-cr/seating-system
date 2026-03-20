from django.urls import path
from .views import create_exam, list_exams, delete_exam

urlpatterns = [
    path("create/", create_exam),
    path("list/", list_exams),
    path("delete/<int:exam_id>/", delete_exam),
]
