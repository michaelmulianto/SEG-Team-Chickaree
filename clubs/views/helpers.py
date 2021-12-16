"""Functions to aid functionality of the views"""
from django.core.exceptions import ObjectDoesNotExist
from clubs.models import Club, Membership, Organiser, Participant
from clubs.views.decorators import is_head_organiser


def is_user_officer_of_club(user, club):
    return Membership.objects.filter(user=user, club=club, is_officer=True).exists()

def is_user_owner_of_club(user, club):
    return Membership.objects.filter(user=user, club=club, is_owner=True).exists()

def is_user_member_of_club(user, club):
    return Membership.objects.filter(user=user, club=club).exists()

def is_user_organiser_of_tournament(user, tournament):
    try:
        possible_organiser_member = Membership.objects.get(club = tournament.club, user = user)
    except(ObjectDoesNotExist):
        return False
    else:
        return Organiser.objects.filter(member = possible_organiser_member, tournament = tournament).exists()

def is_lead_organiser_of_tournament(user, tournament):
    try:
        possible_organiser_member = Membership.objects.get(club = tournament.club, user = user)
    except(ObjectDoesNotExist):
        return False
    else:
        return Organiser.objects.filter(member = possible_organiser_member, tournament = tournament, is_lead_organiser = True).exists()

def is_participant_in_tournament(user, tournament):
    try:
        possible_organiser_member = Membership.objects.get(club = tournament.club, user = user)
    except(ObjectDoesNotExist):
        return False
    else:
        return Participant.objects.filter(member = possible_organiser_member, tournament = tournament).exists()

def sort_clubs(param, order):
    if order == None:
        clubs = Club.objects.all()
    elif order == "asc":
        clubs = Club.objects.order_by(param)
        order = "des"
    elif order == "des":
        clubs = Club.objects.order_by("-" + param)
        order = "asc"
    return clubs

def sort_clubs_for_as_set_of_clubs(clubs, param, order):
    if order == None:
        clubs = clubs
    elif order == "asc":
        clubs = clubs.order_by(param)
        order = "des"
    elif order == "des":
        clubs = clubs.order_by("-" + param)
        order = "asc"
    return clubs
