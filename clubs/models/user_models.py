"""Models related to registered users independent of clubs."""

from libgravatar import Gravatar
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    """Model for a registered user, independent of any clubs."""
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
    REQUIRED_FIELDS = ['username'] # Required fields for a user creation. e.g. when creating a superuser.

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