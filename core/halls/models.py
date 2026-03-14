from django.db import models
from django.conf import settings

# Create your models here.

class Hall(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="halls",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=50)
    rows = models.IntegerField()
    columns = models.IntegerField()
    seats_per_bench = models.IntegerField()

    def __str__(self):
        return self.name

    @property
    def capacity(self):
        return self.rows * self.columns * self.seats_per_bench
