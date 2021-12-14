"""
Models intended to be treated as abstract, and not instantiated.

If we were to set them as abstract we would not be able to query them or set constraints.

Dependencies for helper functions are imported within those helpers.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint

from .tournament_models import Tournament
from .club_models import Membership

class RoundOfMatches(models.Model):
    """Model for collecting together all models that control a set of matches."""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, unique=False, blank=False)

class StageMethodInterface(models.Model):
    class Meta:
        abstract = True

    def get_winners(self):
        raise NotImplementedError

    def get_matches(self):
        from .round_models import Match
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

class TournamentStageBase(RoundOfMatches):
    """Model for single round in the tournament."""
    round_num = models.IntegerField(default = 1, blank = False)

    def get_stage(self):
        if hasattr(self, 'knockoutstage'):
            return self.knockoutstage
        elif hasattr(self, 'groupstage'):
            return self.groupstage
        else:
            return None

    class Meta:
        ordering = ['tournament']