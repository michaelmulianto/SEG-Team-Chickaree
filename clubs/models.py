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
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.db.models import Max
from itertools import combinations

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

class Club(models.Model):
    """Model representing a single chess club."""
    name = models.CharField(max_length=50, blank=False, unique = True)
    location = models.CharField(max_length=50, blank=False)
    description =  models.CharField(max_length=280, blank=False)
    #Automatically use current time as the club creation date
    created_on = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        return f'{self.name}'

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
        return f'User: {self.user.first_name} {self.user.last_name} to Club: {self.club}'

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
        return f'User: {self.user.first_name} {self.user.last_name} from Club: {self.club}'

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
    club = models.ForeignKey(Club, on_delete=models.CASCADE, unique=False, blank=False)
    name = models.CharField(max_length=50, blank=False, unique = True)
    description =  models.CharField(max_length=280, blank=False)
    capacity = models.PositiveIntegerField(default=16, blank=False, validators=[MinValueValidator(2), MaxValueValidator(96)])
    deadline = models.DateTimeField(default=now, auto_now=False, auto_now_add=False, blank=False)
    start = models.DateTimeField(default=now, auto_now=False, auto_now_add=False, blank=False)
    end = models.DateTimeField(default=now, auto_now=False, auto_now_add=False, blank=False)

    def __str__(self):
        return f'{self.name} by {self.club}'

    class Meta:
        ordering = ['start']

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)
        if self.capacity > 16 and ((self.capacity % 4 != 0) or (self.capacity % 6 != 0)) and self.capacity !=32:
            raise ValidationError("The capacity should be divisible by both 4 and 6 when above 16 (except 32).")
        if self.capacity > 32 and (self.capacity % 8 != 0):
            raise ValidationError("The capacity should be divisible by 8 when above 32.")
        if self.capacity < Participant.objects.filter(tournament=self).count():
            raise ValidationError("At no point can there be more participants than capacity.")
        if self.deadline > self.start:
            raise ValidationError("The deadline date cannot be after the start!")
        if self.start > self.end:
            raise ValidationError("The tournament should have a positive duration.")

    def get_current_round(self):
        rounds = StageInterface.objects.filter(tournament=self)
        if rounds.count() == 0:
            return None 
        curr_round_num = rounds.aggregate(Max('round_num'))['round_num__max']
        curr_round = rounds.get(round_num=curr_round_num)
        if hasattr(curr_round, 'knockoutstage'):
            return curr_round.knockoutstage
        else:
            return curr_round.groupstage

    def get_num_participants(self):
        return Participant.objects.filter(tournament=self).count()

    def get_max_round_num(self):
        n = self.get_num_participants()
        if n > 32:
            return 6
        elif n > 16:
            return 5
        else:
            d = 0
            while n > 1:
                d += 1
                n = n/2
            return d

    def generate_next_round(self):
        self.full_clean() # Constraints are needed for this to work.
        curr_round = self.get_current_round()
        if curr_round != None:
            participants = curr_round.get_winners()
            next_num = curr_round.round_num+1
        else: # No round has occured yet.
            participants = list(Participant.objects.filter(tournament=self))
            next_num = 1

        num_participants = len(participants)
        if num_participants < 2:
            return None # Round not complete, no one signed up, or tourney complete

        # KNOCKOUT CASE
        if num_participants <= 16 and (num_participants & (num_participants - 1) == 0):
            my_stage = KnockoutStage.objects.create(
                round_num = next_num,
                tournament=self
            )
            i = 0
            while i < num_participants:
                (Match.objects.create(
                    collection = my_stage,
                    white_player = participants[i],
                    black_player = participants[i+1]
                )).save()
                i += 2
        # GROUP STAGE CASE
        else:
            my_stage = GroupStage.objects.create(
                round_num = next_num,
                tournament=self
            )
            # By own constraints, this will result in a valid draw.
            if num_participants < 33:
                group_size = 4
                required_winners = 16
            else:
                group_size = 6
                required_winners = 32

            num_groups = num_participants // group_size
            winners_per_group = required_winners // num_groups

            for i in range(0, num_groups):
                group = SingleGroup.objects.create(
                    group_stage = my_stage,
                    winners_required = winners_per_group
                )
                group_members = participants[:group_size]
                participants = participants[group_size:]

                player_pairs = combinations(group_members, 2)

                for pair in player_pairs:
                    (Match.objects.create(
                        collection = group,
                        white_player = pair[0],
                        black_player = pair[1]
                    )).save()

                group.full_clean()
                group.save()

        my_stage.full_clean()
        my_stage.save()
        return my_stage


class MemberTournamentRelationship(models.Model):
    """Represent a single relationship between a member of a club and its tournament."""
    member = models.ForeignKey(Membership, on_delete=models.CASCADE, unique=False, blank=False)
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
    """Relationship between member and tournament where member has an admin role."""
    is_lead_organiser = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.member.user.first_name} {self.member.user.last_name} organising {self.tournament.name} by {self.tournament.club}'

class Participant(MemberTournamentRelationship):
    """Relationship between member and tournament where member will play."""
    round_eliminated = models.IntegerField(default=-1)
    joined = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        return f'{self.member.user.first_name} {self.member.user.last_name} in {self.tournament.name} by {self.tournament.club}'

class GenericRoundOfMatches(models.Model):
    """Model for some group of matches together that, when complete, produce some winners."""
    # ABSTRACT, but we can't declare this as we want to define a relation with it.

    def get_winners(self):
        return None

    def get_matches(self):
        return Match.objects.filter(collection=self)

    # 1 entry in list per match player is in
    def get_player_occurences(self):
        matches = self.get_matches()
        player_occurences = []
        for match in matches:
            player_occurences.append(match.white_player)
            player_occurences.append(match.black_player)

        return player_occurences

    def get_is_complete(self):
        return not self.get_matches().filter(result = 0).exists()

class StageInterface(GenericRoundOfMatches):
    # ABSTRACT, but we can't declare it so as we want to query it.
    """Model for single round in the tournament."""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, unique=False, blank=False)
    round_num = models.IntegerField(default = 1, blank = False)

    class Meta:
        ordering = ['tournament']

    # def save(self, *args, **kwargs):
    #     # Due to complex nature of the models it is important that we check validation.
    #     self.full_clean()
    #     super().save()

class Match(models.Model):
    """Model representing a single game of chess, in some tournament stage."""
    white_player = models.ForeignKey(Participant, on_delete=models.CASCADE, unique=False, blank=False, related_name='white')
    black_player = models.ForeignKey(Participant, on_delete=models.CASCADE, unique=False, blank=False, related_name='black')

    collection = models.ForeignKey(GenericRoundOfMatches, on_delete=models.CASCADE, unique=False, blank=False)

    OUTCOMES = (
        (0, 'Incomplete'),
        (1,'White Victory'),
        (2, 'Black Victory'),
        (3, 'Stalemate'),
    )
    result = models.IntegerField(default = 0, choices = OUTCOMES, blank = False)

    class Meta:
        ordering = ['collection']
        constraints = [
            CheckConstraint(
                name='cannot_play_self',
                check=~Q(white_player=F('black_player')),
            ),
        ]

class KnockoutStage(StageInterface):
    """Tournament round of type knockout."""
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
            return None

        matches = self.get_matches()
        winners = []
        for match in matches:
            if match.result == 1:
                winners.append(match.white_player)
                match.black_player.round_eliminated = self.round_num
            elif match.result == 2:
                winners.append(match.black_player)
                match.white_player.round_eliminated = self.round_num
        # Case draw not considered: To-do
        return winners

class GroupStage(StageInterface):
    """Tournament round of type group. Is associated with multiple groups."""
    def get_winners(self):
        if not self.get_is_complete():
            return None

        groups = list(SingleGroup.objects.filter(group_stage=self))
        winners = []
        for group in groups:
            winners += group.get_winners()

        return winners

    def get_is_complete(self):
        groups = list(SingleGroup.objects.filter(group_stage=self))
        for group in groups:
            if not group.get_is_complete():
                return False
        return True

    def full_clean(self):
        super().full_clean()
        if SingleGroup.objects.filter(group_stage=self).count() < 1:
            raise ValidationError("No groups assigned to the stage!")

class SingleGroup(GenericRoundOfMatches):
    """Represent a single round robin group within a larger group stage."""
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

    def get_is_complete(self):
        matches = self.get_matches()
        for match in matches:
            if match.result == 0:
                return False
        return True

    def get_winners(self):
        if not self.get_is_complete():
            return None

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
        winner_ids = []
        for i in range(0,self.winners_required):
            winner_ids.append(res[i])

        loser_ids = []
        for i in range(self.winners_required, len(res)):
            loser_ids.append(res[i])

        winners = []
        for p_id in winner_ids:
            winners.append(Participant.objects.get(id = p_id))

        for p_id in loser_ids:
            Participant.objects.filter(id = p_id).round_eliminated = self.group_stage.round_num

        return winners
