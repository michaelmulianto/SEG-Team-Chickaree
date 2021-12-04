"""Functions to aid functionality of the views"""
from clubs.models import User, Club, Member, Application, Ban

def is_user_officer_of_club(user, club):
    return Member.objects.filter(user=user, club=club, is_officer=True).exists()

def is_user_owner_of_club(user, club):
    return Member.objects.filter(user=user, club=club, is_owner=True).exists()

def get_clubs_of_user(userIn):
    my_clubs = []
    for club in Club.objects.all():
        if Application.objects.filter(club=club, user=userIn):
            my_clubs.append(club)
        if Member.objects.filter(club=club, user=userIn):
            my_clubs.append(club)

    return my_clubs
