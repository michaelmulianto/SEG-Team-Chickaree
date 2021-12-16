"""Functions to aid functionality of the views"""
from django.core.exceptions import ObjectDoesNotExist
from clubs.models import Club, Membership, Organiser, Participant
from django.db.models.functions import Lower


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
    if order == "asc":
        clubs = Club.objects.all().order_by(Lower(param))
        order = "des"
    elif order == "des":
        clubs = Club.objects.all().order_by(Lower(param).desc())
        order = "asc"
    else:
        clubs = Club.objects.all()
    return clubs
