"""
Django provides many built in tags to use within templates but some may be
missing and they are implemented here.

In addition, functions in templates cannot take parameters so when a method
would need to more than one parameter it may be implemented here to avoid
passing in many variables in the view.
"""

from django import template
from clubs.models import Club, Application, Membership, Participant, Organiser
register = template.Library()

# BASIC tags

@register.simple_tag
def boolean_or(a, b):
    return a or b


# CLUB tags

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


# TOURNAMENT tags

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
