"""
Define the models for the system.

Implemented:
    - User
    - Club
    - Application: many clubs to many users
    - Member: many clubs to many users
"""

from libgravatar import Gravatar
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint, CheckConstraint, Q, F, Exists
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

class Member(models.Model):
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
        if Member.objects.exclude(id=self.id).filter(club=self.club, is_owner=True).exists() and self.is_owner:
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
    pass 

class MemberTournamentRelationship(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, unique=False, blank=False)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, unique=False, blank=False)

    class Meta:
        ordering = ['tournament']
        constraints = [
            UniqueConstraint(
                name='one_object_per_relationship',
                fields=['member', 'tournament'],
            ),
        ]

class Organiser(MemberTournamentRelationship):
    is_lead_organiser = models.BooleanField(default=False)

class Participant(MemberTournamentRelationship):
    round_eliminated = models.IntegerField(default=-1)

class StageInterface(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, unique=False, blank=False)
    round_num = models.IntegerField(default = 1, blank = False)

    class Meta:
        ordering = ['tournament']

    # ABSTRACT
    def get_winners(self):
        return []

    def get_next_round(self):
        participants = self.get_winners()
        num_participants = len(participants)
        if(num_participants < 1):
            return None
        
        if(num_participants > 16):
            pass
            #CREATE GROUP
        elif(num_participants & (num_participants - 1) != 0):
            pass
            #CREATE GROUP
        else:
            pass
            #create knockout

    def get_matches(self):
        return Match.objects.filter(stage=self)

    # 1 entry in list per player
    def get_player_occurences(self):
        matches = self.get_matches()
        player_occurences = []
        for match in matches:
            player_occurences.append(match.white_player)
            player_occurences.append(match.black_player)

        return player_occurences

    def get_is_complete(self):
        return not self.get_matches().filter(result = None).exists()

    def full_clean(self):
        super().full_clean()
        if self.get_matches().count() < 1:
            raise ValidationError("A stage cannot have no matches.")

    def save(self):
        # Due to complex nature of the models it is important that we check validation.
        self.full_clean()
        super().save()

class Match(models.Model):
    white_player = models.ForeignKey(Participant, on_delete=models.CASCADE, unique=False, blank=False, related_name='white')
    black_player = models.ForeignKey(Participant, on_delete=models.CASCADE, unique=False, blank=False, related_name='black')

    stage = models.ForeignKey(StageInterface, on_delete=models.CASCADE, unique=False, blank=False)

    OUTCOMES = (
        (1,'White Victory'),
        (2, 'Black Victory'),
        (3, 'Stalemate'),
    )
    result = models.IntegerField(default = None, choices = OUTCOMES, blank = True)

    class Meta:
        ordering = ['stage']
        constraints = [
            UniqueConstraint(
                name='cannot_play_self',
                fields=['white_player', 'black_player'],
            ),
        ]

class KnockoutStage(StageInterface):

    def full_clean(self):
        super().full_clean()
        matches = self.get_matches()

        # Using len is more efficient here as we intend to traverse the query set later.
        if (len(matches) & (len(matches) - 1) != 0):
            raise ValidationError("The number of matches must be a power of two.")

        player_occurences = self.get_player_occurences()

        if(len(player_occurences) != len(set(player_occurences))):
            raise ValidationError("Each player must only play 1 match.")

    def get_winners(self):
        if not self.get_is_complete():
            return []

        matches = self.get_matches()
        winners = []
        for match in matches:
            if match.result == 1:
                winners.append(match.white_player)
            elif match.result == 2:
                winners.append(match.black_player)
        # Case draw not considered: To-do
        return winners

class GroupStage(StageInterface):
    def get_next_round(self):
        pass

class SingleGroup(StageInterface):
    group_stage = models.ForeignKey(GroupStage, on_delete=models.CASCADE, unique=False, blank=False)
    winners_required = models.IntegerField(default = 1, blank=False)

    def full_clean(self):
        super().full_clean()
        player_occurences = self.get_player_occurences()

        # We must calculate the number of players each player plays.
        unique_players = set(player_occurences)
        num_players = len(unique_players)

        num_occurences = {}
        for player in unique_players:
            num_occurences.update({player.id : 0})

        for occurence in player_occurences:
            num_occurences.update({occurence.id : num_occurences[occurence.id]+1})

        # Now we ensure all players have played exactly n-1 games i.e. everyone once
        for k in num_occurences.values():
            if k != num_players-1:
                raise ValidationError("Not all players play the correct number of games.")

        # Check total number of matches, in case of edge case.
        if self.get_matches().count() != ((num_players-1)/2.0) * num_players: # Triangle number: (n/2)*(n+1)
            raise ValidationError("The incorrect number of matches are linked to this group.")
            

    def get_winners(self):
        if not self.get_is_complete():
            return []

        matches = self.get_matches()
        players = set(self.get_player_occurences())
        scores = {}
        for player in players:
            scores.update({player.id:0})

        for match in matches:
            if match.result == 1:
                scores[match.white_player.id] += 1
            elif match.result == 2:
                scores[match.black_player.id] += 1
            else:
                scores[match.white_player.id] += 0.5
                scores[match.black_player.id] += 0.5

        # https://www.geeksforgeeks.org/python-sort-list-by-dictionary-values/
        res = sorted(scores.keys(), key = lambda ele: scores[ele])
        return res[self.num_winners + 1]
