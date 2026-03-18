from django.db import models
from django.conf import settings

# Create your models here.

class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.code


class Student(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="students",
        null=True,
        blank=True
    )
    register_no = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    semester = models.IntegerField(null=True, blank=True)
    subject_code = models.CharField(max_length=20, null=True, blank=True)
    subjects = models.ManyToManyField(Subject, blank=True, related_name="students")

    def __str__(self):
        return self.register_no

    class Meta:
        unique_together = ("user", "register_no")


class UploadHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_uploads"
    )
    file_name = models.CharField(max_length=255)
    students_count = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file_name}"
