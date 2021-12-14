from django import template
from datetime import datetime
from clubs.models import User, Club, Application, Membership, Ban, Participant, Organiser, Tournament, SingleGroup, Match
register = template.Library()

@register.simple_tag
def boolean_or(a, b):
    return a or b

@register.simple_tag
def get_clubs(current_user):
    my_clubs = []
    for club in Club.objects.all():
        if Membership.objects.filter(club=club, user=current_user):
            my_clubs.append(club)
    return my_clubs

@register.simple_tag
def check_is_organiser(user, tournament):
    if Membership.objects.filter(user=user, club=tournament.club).exists():
        membership = Membership.objects.get(user=user, club=tournament.club)
        return Organiser.objects.filter(member=membership, tournament=tournament).exists()
    else:
        return False

@register.simple_tag
def check_is_lead_organiser(user, tournament):
    if Membership.objects.filter(user=user, club=tournament.club).exists():
        membership = Membership.objects.get(user=user, club=tournament.club)
        return Organiser.objects.filter(member=membership, tournament=tournament, is_lead_organiser = True).exists()
    else:
        return False

@register.simple_tag
def check_has_joined_tournament(user, tournament):
    if Membership.objects.filter(user=user, club=tournament.club).exists():
        membership = Membership.objects.get(user=user, club=tournament.club)
        return Participant.objects.filter(member=membership, tournament=tournament).exists()
    else:
        return False

@register.simple_tag
def check_has_applied(club_to_check, user):
    return Application.objects.filter(club=club_to_check, user=user).exists()

@register.simple_tag
def check_is_member(club_to_check, user):
    return Membership.objects.filter(club=club_to_check, user=user).exists()

@register.simple_tag
def check_is_officer(club_to_check, user):
    return Membership.objects.filter(club=club_to_check, user=user, is_officer=True).exists()

@register.simple_tag
def check_is_owner(club_to_check, user):
    return Membership.objects.filter(club=club_to_check, user=user, is_owner=True).exists()



@register.simple_tag
def check_is_lead_organiser(user, tournament):
    if Membership.objects.filter(user=user, club=tournament.club).exists():
        membership = Membership.objects.get(user=user, club=tournament.club)
        return Organiser.objects.filter(member=membership, tournament=tournament).exists()
    return False

@register.simple_tag
def check_has_joined_tournament(user, tournament):
    if Membership.objects.filter(user=user, club=tournament.club).exists():
        membership = Membership.objects.get(user=user, club=tournament.club)
        return Participant.objects.filter(member=membership, tournament=tournament).exists()
    return False
@register.simple_tag
def get_single_groups(group_stage):
    return SingleGroup.objects.filter(group_stage=group_stage)

@register.simple_tag
def get_matches(stage):
    return Match.objects.filter(collection=stage)

@register.simple_tag
def get_standings(single_group):
        if not single_group.get_is_complete():
            return None

        matches = single_group.get_matches()
        players = set(single_group.get_player_occurrences())
        scores = {}
        matches_played = {}
        for player in players:
            scores.update({player.id:0})
            matches_played.update({player.id:0})

        for match in matches:
            if match.result == 1:
                scores[match.white_player.id] += 1
            elif match.result == 2:
                scores[match.black_player.id] += 1
            else:
                scores[match.white_player.id] += 0.5
                scores[match.black_player.id] += 0.5

            matches_played[match.white_player.id] += 1
            matches_played[match.black_player.id] += 1

        # https://www.geeksforgeeks.org/python-sort-list-by-dictionary-values/
        ordered_scores = dict(sorted(scores.items(), key = lambda item: item[1]))

        standings = []
        for participant in ordered_scores.keys():
            standing = [Participant.objects.get(id=participant), ordered_scores[participant], matches_played[participant]]
            standings.append(standing)

        return list(reversed(standings))
