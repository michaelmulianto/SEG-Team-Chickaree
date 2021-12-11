from django import template
from datetime import datetime
from clubs.models import User, Club, Application, Membership, Ban, Participant, Organiser, Tournament
register = template.Library()

@register.simple_tag
def count_members(club_to_count):
    return Membership.objects.filter(club=club_to_count).count()

@register.simple_tag
def count_participants(tournament):
    return Participant.objects.filter(tournament=tournament).count()



@register.simple_tag
def get_clubs(current_user):
    my_clubs = []
    for club in Club.objects.all():
        if Membership.objects.filter(club=club, user=current_user):
            my_clubs.append(club)
    return my_clubs

@register.simple_tag
def check_is_lead_organiser(user, tournament):
    if Membership.objects.filter(user=user, club=tournament.club).exists():
        membership = Membership.objects.get(user=user, club=tournament.club)
        return Organiser.objects.filter(member=membership, tournament=tournament).exists()
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
def get_members(club):
    return Membership.objects.filter(club=club)

@register.simple_tag
def get_banned_members(club):
    return Ban.objects.filter(club=club)

@register.simple_tag
def get_applications(club):
    return Application.objects.filter(club=club)

@register.simple_tag
def get_officers(club):
    return Membership.objects.filter(club=club, is_officer=True)

@register.simple_tag
def get_owner(club):
    return Membership.objects.get(club=club, is_owner=True)



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