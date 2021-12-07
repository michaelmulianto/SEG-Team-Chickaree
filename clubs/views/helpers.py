"""Functions to aid functionality of the views"""
from clubs.models import User, Club, Membership, Application, Ban

def is_user_officer_of_club(user, club):
    return Membership.objects.filter(user=user, club=club, is_officer=True).exists()

def is_user_owner_of_club(user, club):
    return Membership.objects.filter(user=user, club=club, is_owner=True).exists()

def get_clubs_of_user(userIn):
    my_clubs = []
    for club in Club.objects.all():
        if Application.objects.filter(club=club, user=userIn):
            my_clubs.append(club)
        if Membership.objects.filter(club=club, user=userIn):
            my_clubs.append(club)

    return my_clubs

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