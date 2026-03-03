from django.db import models

# Create your models here.

from django.db import models
from exams.models import Exam
from halls.models import Hall
from students.models import Student


class SeatingAllocation(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exam.name} - {self.created_at}"


class Seat(models.Model):
    allocation = models.ForeignKey(SeatingAllocation, on_delete=models.CASCADE)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    row = models.IntegerField()
    column = models.IntegerField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.hall.name} ({self.row},{self.column})"