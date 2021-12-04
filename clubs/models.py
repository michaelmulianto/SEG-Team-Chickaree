"""
Define the models for the system.

Implemented:
    - User
    - Club
    - Application: many clubs to many users
    - Member: many clubs to many users
"""

from libgravatar import Gravatar
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    """Model for a registered user, independent of any clubs"""
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
            RegexValidator(regex=r'^[a-zA-Z\'\-]{1,}$'),
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

    bio = models.CharField(max_length=520, blank = True, default = '')

    LEVELS = (
        (1,'Beginner'),
        (2, 'Intermediate'),
        (3, 'Advanced'),
    )
    experience = models.IntegerField(default = 1, choices = LEVELS)

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self, size=50):
        """Return a URL to the user's small gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

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
    """Model representing a membership of some single chess club by some single user"""
    club = models.ForeignKey('Club', on_delete=models.CASCADE, unique=False, blank=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE, unique=False, blank=False)
    is_officer = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)

    class Meta:
        ordering = ['club']
        unique_together = ("club", "user") #Contraint: No user is twice in the same club.


class Application(models.Model):
    """Model for an application to a club by some user."""
    club = models.ForeignKey(Club, on_delete=models.CASCADE, unique=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, blank=False)
    personal_statement = models.CharField(max_length=580, blank=False, default = "")

    class Meta:
        ordering = ['club']
        unique_together = ("club", "user")

class Ban(models.Model):
    "Medel for a ban to a club for some user"
    club = models.ForeignKey(Club, on_delete=models.CASCADE, unique=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, blank=False)
