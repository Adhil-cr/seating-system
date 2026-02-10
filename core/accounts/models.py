from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"

    ROLE_CHOICES = [
        (SUPER_ADMIN, "Super Admin"),
        (ADMIN, "Admin"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ADMIN
    )

    def __str__(self):
        return self.username
