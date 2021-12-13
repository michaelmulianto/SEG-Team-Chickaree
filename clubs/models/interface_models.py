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

class GenericRoundOfMatches(models.Model):
    """Model for some group of matches together that, when complete, produce some winners."""
    def get_winners(self):
        return None

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

class StageInterface(GenericRoundOfMatches):
    """Model for single round in the tournament."""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, unique=False, blank=False)
    round_num = models.IntegerField(default = 1, blank = False)

    def get_round(self):
        if hasattr(curr_round, 'knockoutstage'):
            return curr_round.knockoutstage
        elif hasattr(curr_round, 'groupstage'):
            return curr_round.groupstage
        else:
            return None

    class Meta:
        ordering = ['tournament']