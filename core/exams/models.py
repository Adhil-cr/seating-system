from django.db import models
from django.conf import settings

# Create your models here.
from students.models import Subject

class Exam(models.Model):
    SESSION_AM = "AM"
    SESSION_PM = "PM"
    SESSION_CHOICES = [
        (SESSION_AM, "AM"),
        (SESSION_PM, "PM"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exams",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    date = models.DateField()
    session = models.CharField(
        max_length=2,
        choices=SESSION_CHOICES,
        default=SESSION_AM
    )
    subject_codes = models.JSONField(default=list, blank=True)
    subjects = models.ManyToManyField(Subject, blank=True)

    def __str__(self):
        return self.name
