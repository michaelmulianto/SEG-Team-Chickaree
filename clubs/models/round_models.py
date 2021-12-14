"""Models related to a single round in a tournament."""
from libgravatar import Gravatar
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CheckConstraint, Q, F

from .interface_models import RoundOfMatches, StageMethodInterface
from .tournament_models import Participant

class Match(models.Model):
    """Model representing a single game of chess, in some tournament stage."""
    white_player = models.ForeignKey(Participant, on_delete=models.CASCADE, unique=False, blank=False, related_name='white')
    black_player = models.ForeignKey(Participant, on_delete=models.CASCADE, unique=False, blank=False, related_name='black')

    collection = models.ForeignKey(RoundOfMatches, on_delete=models.CASCADE, unique=False, blank=False)

    OUTCOMES = [
        (0, 'Incomplete'),
        (1,'White Victory'),
        (2, 'Black Victory'),
        (3, 'Stalemate'),
    ]
    result = models.IntegerField(default = 0, choices = OUTCOMES, blank = False)

    class Meta:
        ordering = ['collection']
        constraints = [
            CheckConstraint(
                name='cannot_play_self',
                check=~Q(white_player=F('black_player')),
            ),
        ]

class KnockoutStage(TournamentStageBase, StageMethodInterface):
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

class GroupStage(TournamentStageBase, StageMethodInterface):
    """Tournament round of type group. Is associated with multiple groups."""
    def get_winners(self):
        if not self.get_is_complete():
            return None

        groups = list(SingleGroup.objects.filter(group_stage=self))
        winners = []
        for group in groups:
            winners += group.get_winners()

        return winners

    def get_matches(self):
        groups = list(SingleGroup.objects.filter(group_stage=self))
        matches = []
        for group in groups:
            matches += group.get_matches()
        return matches

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

class SingleGroup(RoundOfMatches):
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