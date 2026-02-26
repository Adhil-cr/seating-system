from django.db import models

# Create your models here.

from django.db import models

class Hall(models.Model):
    name = models.CharField(max_length=50)
    rows = models.IntegerField()
    columns = models.IntegerField()
    seats_per_bench = models.IntegerField()

    def __str__(self):
        return self.name

    @property
    def capacity(self):
        return self.rows * self.columns * self.seats_per_bench