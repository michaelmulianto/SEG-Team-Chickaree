"""Models related to a single round in a tournament."""
from libgravatar import Gravatar
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CheckConstraint, Q, F

from .interface_models import RoundOfMatches, StageMethodInterface, TournamentStageBase
from .tournament_models import Participant

class Match(models.Model):
    """Model representing a single game of chess, in some tournament stage."""
    white_player = models.ForeignKey(Participant, on_delete=models.CASCADE, unique=False, blank=False, related_name='white')
    black_player = models.ForeignKey(Participant, on_delete=models.CASCADE, unique=False, blank=False, related_name='black')

    collection = models.ForeignKey(RoundOfMatches, on_delete=models.CASCADE, unique=False, blank=False)

    class Result(models.IntegerChoices):
        Incomplete = 0, 'Incomplete'
        White_Victory = 1, f'White Victory'
        Black_Victory = 2, f'Black Victory'
        Stalemate = 3, 'Stalemate'

    result = models.IntegerField(default = 0, choices = Result.choices, blank = False)

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

        player_occurrences = self.get_player_occurrences()

        if(len(player_occurrences) != len(set(player_occurrences))):
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
                match.black_player.save()
            elif match.result == 2:
                winners.append(match.black_player)
                match.white_player.round_eliminated = self.round_num
                match.white_player.save()
        # Case draw not considered: To-do
        return winners

class GroupStage(TournamentStageBase, StageMethodInterface):
    """Tournament round of type group. Is associated with multiple groups."""
    def get_winners(self):
        if not self.get_is_complete():
            return None

        # We assume the number of winners is even, with the current algorithms this should always be the case.
        
        groups = list(self.get_single_groups())
        winners_per_group = groups[0].winners_required
        num_winners = len(groups)*winners_per_group
        seeds = []
        for i in range(winners_per_group):
            seeds.append([])
            
        for group in groups:
            winners_from_group = group.get_winners()
            for i in range(winners_per_group):
                seeds[i].append(winners_from_group[i])
                
        winners = []
        for i in range(winners_per_group):
            # 'Clever' use of modulo to seperate those in the same group.
            # We also ensure 2 players in the same seed are not adjacent.
            for j in range(len(groups)):
                winners.append(seeds[(i+j)%winners_per_group][j])
        
        return winners

    def get_matches(self):
        groups = list(self.get_single_groups())
        matches = []
        for group in groups:
            matches += group.get_matches()
        return matches

    def get_single_groups(self):
        return SingleGroup.objects.filter(group_stage=self)

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

class SingleGroup(RoundOfMatches, StageMethodInterface):
    """Represent a single round robin group within a larger group stage."""
    group_stage = models.ForeignKey(GroupStage, on_delete=models.CASCADE, unique=False, blank=False)
    winners_required = models.IntegerField(default = 1, blank=False)

    def save(self, *args, **kwargs):
        self.tournament = self.group_stage.tournament
        super().save(*args, **kwargs)

    def full_clean(self):
        super().full_clean()
        player_occurrences = self.get_player_occurrences()

        # We must calculate the number of players each player plays.
        unique_players = set(player_occurrences)
        num_players = len(unique_players)

        num_occurrences = {}
        for player in unique_players:
            num_occurrences.update({player.id : 0})

        for occurrence in player_occurrences:
            num_occurrences.update({occurrence.id : num_occurrences[occurrence.id]+1})

        # Now we ensure all players have played exactly n-1 games i.e. everyone once
        for k in num_occurrences.values():
            if k != num_players-1:
                raise ValidationError("Not all players play the correct number of games.")

        # Check total number of matches, in case of edge case.
        if self.get_matches().count() != ((num_players-1)/2.0) * num_players: # Triangle number: (n/2)*(n+1)
            raise ValidationError("The incorrect number of matches are linked to this group.")

    def get_standings(self):
        matches = self.get_matches()
        players = set(self.get_player_occurrences())
        scores = {}
        matches_played = {}
        for player in players:
            scores.update({player.id:0})
            matches_played.update({player.id:0})

        for match in matches:
            # Add points to total for each played match
            if match.result == 1:
                scores[match.white_player.id] += 1
            elif match.result == 2:
                scores[match.black_player.id] += 1
            elif match.result == 3:
                scores[match.white_player.id] += 0.5
                scores[match.black_player.id] += 0.5

            # Add 1 to matches played if result is not incomplete
            if not match.result == 0:
                matches_played[match.white_player.id] += 1
                matches_played[match.black_player.id] += 1

        # https://www.geeksforgeeks.org/python-sort-list-by-dictionary-values/
        ordered_scores = dict(sorted(scores.items(), key = lambda item: item[1]))

        standings = []
        for participant in ordered_scores.keys():
            standing = [Participant.objects.get(id=participant), ordered_scores[participant], matches_played[participant]]
            standings.append(standing)

        return list(reversed(standings))

    def get_winners(self):
        if not self.get_is_complete():
            return None

        standings = self.get_standings()
        
        winners_standings = standings[:self.winners_required]
        losers_standings = standings[self.winners_required:]
        
        winners=[]
        for entry in winners_standings:
            winners.append(entry[0])

        for entry in losers_standings:
            entry[0].round_eliminated = self.group_stage.round_num
            entry[0].save()

        return winners
