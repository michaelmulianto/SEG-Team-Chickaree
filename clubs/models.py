"""
Define the models for the system.

Implemented:
    - User
    - Club
    - Application: many clubs to many users
    - Member: many clubs to many users
"""
from datetime import datetime
from django.utils import timezone
from django.utils.timezone import now
from libgravatar import Gravatar
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint, CheckConstraint, Q, F, Exists
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator

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

    USERNAME_FIELD = 'email' # set default auth user to email
    REQUIRED_FIELDS = [] # Django error told me to do this

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

class Membership(models.Model):
    """Model representing a membership of some single chess club by some single user"""
    club = models.ForeignKey('Club', on_delete=models.CASCADE, unique=False, blank=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE, unique=False, blank=False)
    is_officer = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)

    class Meta:
        ordering = ['club']
        constraints = [
            UniqueConstraint(
                name='user_in_club_unique',
                fields=['club', 'user'],
            ),
        ]

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)
        if Membership.objects.exclude(id=self.id).filter(club=self.club, is_owner=True).exists() and self.is_owner:
            raise ValidationError("There is already an owner for this club.")

        if self.is_owner and self.is_officer:
            raise ValidationError("A single member cannot be both member and officer.")


class Application(models.Model):
    """Model for an application to a club by some user."""
    club = models.ForeignKey(Club, on_delete=models.CASCADE, unique=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, blank=False)
    personal_statement = models.CharField(max_length=580, blank=False, default = "")

    class Meta:
        ordering = ['club']
        constraints = [
            UniqueConstraint(
                name='application_to_club_unique',
                fields=['club', 'user'],
            )
        ]

class Ban(models.Model):
    "Model for a ban to a club for some user"
    club = models.ForeignKey(Club, on_delete=models.CASCADE, unique=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, blank=False)

    class Meta:
        ordering = ['club']
        constraints = [
            UniqueConstraint(
                name='user_ban_from_club_unique',
                fields=['club', 'user'],
            )
        ]

class Tournament(models.Model):
    """Model representing a single tournament."""
    name = models.CharField(max_length=50, blank=False, unique = True)
    description =  models.CharField(max_length=280, blank=False)
    capacity = models.PositiveIntegerField(default=16, blank=False)
    start = models.DateTimeField(default=now, auto_now=False, auto_now_add=False, blank=False)
    end = models.DateTimeField(default=now, auto_now=False, auto_now_add=False, blank=False)

    class Meta:
        ordering = ['start']

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)
        if self.capacity < 2:
            raise ValidationError("The capacity should be at least 2.")
        if self.capacity > 96:
            raise ValidationError("The capacity should not exceed 96.")
        if self.capacity % 2 != 0:
            raise ValidationError("The capacity should be even.")
        if self.start < now():
            raise ValidationError("The start date cannot be in the past!")
        if self.end < now():
            raise ValidationError("The end date cannot be in the past!")
        if self.start > self.end:
            raise ValidationError("The tournament should have a positive duration.")

    def get_club():
        pass

    def get_initial_round():
        pass
