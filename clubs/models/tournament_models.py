"""
Models related to the highest abstraction of a tournament.

Contains: Tournament, Organiser and Participant, alongside the latter two's parent model.

Dependencies for helper functions are imported within those helpers.
"""

from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Max
from itertools import combinations

from .club_models import Club, Membership

class Tournament(models.Model):
    """Model representing a single tournament."""
    club = models.ForeignKey(Club, on_delete=models.CASCADE, unique=False, blank=False)
    name = models.CharField(max_length=50, blank=False, unique = False)
    description =  models.CharField(max_length=280, blank=False)
    capacity = models.PositiveIntegerField(default=16, blank=False, validators=[MinValueValidator(2), MaxValueValidator(96)])
    deadline = models.DateTimeField(blank=False)
    start = models.DateTimeField(blank=False)
    end = models.DateTimeField(blank=False)
    created_on = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        return f'{self.name} by {self.club}'

    class Meta:
        ordering = ['start']
        constraints = [
            UniqueConstraint(
                name='tournament_name_must_be_unique_by_club',
                fields=['club', 'name'],
            ),
        ]

    def get_is_complete(self):
        r = self.get_current_round()
        if r != None:
            winners = r.get_winners()
            if winners != None:
                return len(winners)==1
        return False

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

        if self.created_on == None:
            creation_time = now()
        else:
            creation_time = self.created_on

        if self.deadline < creation_time:
            raise ValidationError("Times must be after time of object creation.")

    def get_all_stage_bases(self):
        from .interface_models import TournamentStageBase
        return TournamentStageBase.objects.filter(tournament=self)

    def get_current_round(self):
        rounds = self.get_all_stage_bases()
        if rounds.count() == 0:
            return None
        curr_round_num = rounds.aggregate(Max('round_num'))['round_num__max']
        stage_base_of_round = rounds.get(round_num=curr_round_num)
        return stage_base_of_round.get_stage()

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

        if self.get_is_complete():
            # Whole tournament is complete already
            return None

        curr_round = self.get_current_round()

        if curr_round != None:
            participants = curr_round.get_winners()
            next_num = curr_round.round_num+1
        else: # No round has occured yet.
            participants = list(Participant.objects.filter(tournament=self))
            next_num = 1

        if participants == None:
            # Current round is not yet complete
            return None

        num_participants = len(participants)

        if num_participants == 0:
            # No one joined!!!
            return None

        from .round_models import KnockoutStage, GroupStage, SingleGroup, Match
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
    """Represent a single relationship between a member of a club and its tournament. This is abstract."""
    # We cannot declare this as abstract as we want to apply constraints. Regardless it should not be instantiated individually.
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