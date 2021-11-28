"""
Define the models for the system.

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
    """Model representing a single chess club."""
    name = models.CharField(max_length=50, blank=False, unique = True)
    location = models.CharField(max_length=50, blank=False)
    description =  models.CharField(max_length=280, blank=False)
    #Automatically use current time as the club creation date
    created_on = models.DateTimeField(auto_now_add=True, blank=False)

    class Meta:
        ordering = ['-created_on']


class Member(models.Model):
    """Model representing a member of some single chess club"""
    club = models.ForeignKey('Club', on_delete=models.CASCADE, unique=False, blank=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE, unique=False, blank=False)
    isOfficer = models.BooleanField(default=False)
    isOwner = models.BooleanField(default=False)
    class Meta:
        ordering = ['club']


class Application(models.Model):
    """Model for an application to a club"""
    club = models.ForeignKey(Club, on_delete=models.CASCADE, unique=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, blank=False)
    LEVELS = (
        (1,'Beginner'),
        (2, 'Intermediate'),
        (3, 'Advanced'),
    )
    experience = models.IntegerField(default = 1, choices = LEVELS)
    personal_statement = models.CharField(max_length=580, blank=False, default = "")
