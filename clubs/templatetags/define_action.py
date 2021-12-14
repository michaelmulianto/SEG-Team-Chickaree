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
