"""
Define the models for the system.

Currently implemented models:
    - User
"""
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Model for a generic user, independent of any clubs"""
    username = models.CharField(
    max_length=32,
    unique=True,
    blank=False,
    )

    last_name = models.CharField(
    max_length=48,
    unique=False,
    blank=False
    )

    first_name = models.CharField(
    max_length=48,
    unique=False,
    blank=False,
    )

    email = models.EmailField(
    unique=True,
    blank=False,
    )
