from django.db import models

# Create your models here.

from django.db import models

class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.code


class Student(models.Model):
    register_no = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)

    def __str__(self):
        return self.register_no