from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('supervisor', 'Supervisor'),
        ('employee', 'Employee'),
        ('guest', 'Guest'),
    ]

    name = models.CharField(max_length=100, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')

    def __str__(self):
        return f"{self.name} ({self.role})"
