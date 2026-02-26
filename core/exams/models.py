from django.db import models

# Create your models here.

from django.db import models
from students.models import Subject

class Exam(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    subjects = models.ManyToManyField(Subject)

    def __str__(self):
        return self.name