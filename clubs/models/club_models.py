"""Models related to the base functionality of a chess club."""

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.contrib.auth.models import AbstractUser

from .user_models import User

class Club(models.Model):
    """Model representing a single chess club."""
    name = models.CharField(max_length=50, blank=False, unique = True)
    location = models.CharField(max_length=50, blank=False)
    description =  models.CharField(max_length=280, blank=False)
    #Automatically use current time as the club creation date
    created_on = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        return f'{self.name}'

    def get_memberships(self):
        return Membership.objects.filter(club=self)

    def get_banned_members(self):
        return Ban.objects.filter(club=self)

    def get_applications(self):
        return Application.objects.filter(club=self)

    def get_officers(self):
        return Membership.objects.filter(club=self, is_officer=True)

    def get_owner(self):
        return Membership.objects.get(club=self, is_owner=True)


    class Meta:
        ordering = ['-created_on']

class Membership(models.Model):
    """Model representing a membership of some single chess club by some single user"""
    club = models.ForeignKey('Club', on_delete=models.CASCADE, unique=False, blank=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE, unique=False, blank=False)
    is_officer = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)

    def __str__(self):
        return f'User: {self.user.first_name} {self.user.last_name} at Club: {self.club}'

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

    def __str__(self):
        return f'Applications: {self.user.first_name} {self.user.last_name} to Club: {self.club}'

    class Meta:
        ordering = ['club']
        constraints = [
            UniqueConstraint(
                name='application_to_club_unique',
                fields=['club', 'user'],
            )
        ]

class Ban(models.Model):
    "Model for a ban to a club for some user."
    club = models.ForeignKey(Club, on_delete=models.CASCADE, unique=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, blank=False)

    def __str__(self):
        return f'Ban: {self.user.first_name} {self.user.last_name} from Club: {self.club}'

    class Meta:
        ordering = ['club']
        constraints = [
            UniqueConstraint(
                name='user_ban_from_club_unique',
                fields=['club', 'user'],
            )
        ]
