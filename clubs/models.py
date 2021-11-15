"""
Define the models for the system.

Currently implemented models:
    - User
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    """Model for a generic user, independent of any clubs"""
    username = models.CharField(
    max_length=32,
    unique=True,
    blank=False,
    validators=[
        # Ensure only alphanumerics are used and length is min 3.
        RegexValidator(regex=r'^\w{3,}$'),
    ],
    )

    last_name = models.CharField(
    max_length=48,
    unique=False,
    blank=False,
    validators=[
        # Ensure only letters are used.
        RegexValidator(regex=r'^[a-zA-Z]{1,}$'),
    ],
    )

    first_name = models.CharField(
    max_length=48,
    unique=False,
    blank=False,
    validators=[
        # Ensure only letters are used.
        RegexValidator(regex=r'^[a-zA-Z]{1,}$'),
    ],
    )

    email = models.EmailField(
    unique=True,
    blank=False,
    )

class Club(models.Model):
    #Define foreign key of the club model
    owner = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=50, blank=True, unique = True)
    location = models.CharField(max_length=50, blank=True)
    description =  models.CharField(max_length=280, blank=True)
    #Automatically use current time as the club creation date
    created_on = models.DateTimeField(auto_now_add=True, blank=False)
    class Meta:
        ordering = ['-created_on']
