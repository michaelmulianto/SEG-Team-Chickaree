"""Views relating to viewing a club and general member facing views."""

from django.views import View

from .helpers import get_clubs_of_user
from .decorators import club_exists, membership_exists, club_exists, is_user_owner_of_club
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from django.utils.decorators import method_decorator

from clubs.models import Membership, Club

from django.shortcuts import render, redirect

@login_required
@club_exists
def members_list(request, club_id):
    """Display a list of the members in a club"""
    current_user = request.user
    club = Club.objects.get(id = club_id)
    members = Membership.objects.filter(club = club)
    return render(request, 'members_list.html', {'members': members, 'club': club, 'current_user': current_user , 'my_clubs':get_clubs_of_user(request.user)})


@login_required
@club_exists
def show_club(request, club_id):
    """View details of a club."""
    current_user = request.user
    club = Club.objects.get(id=club_id)
    members = Membership.objects.filter(club = club_id)
    officers = members.filter(is_officer = True)
    officerCount = officers.count()
    getOwner = members.get(is_owner = True)
    numberOfMembers = members.count()
    checkUserisMember = members.filter(user = current_user)
    isMember = False
    isOwner = False
    isOfficer = False
    if checkUserisMember.filter(is_owner = True).count() > 0:
        isOwner = True
    if checkUserisMember.count() > 0:
        isMember = True
    if checkUserisMember.filter(is_officer = True).count() > 0:
        isOfficer = True
    return render(request, 'show_club.html', {'current_user': request.user, 'club': club, 'members': numberOfMembers, 'userIsMember': isMember, 'owner': getOwner, 'userIsOwner': isOwner, 'userIsOfficer': isOfficer, 'officers': officers, 'my_clubs':get_clubs_of_user(request.user), 'officerCount': officerCount})


@login_required
@club_exists
def leave_club(request, club_id):
    """Delete the member object linking the current user to the specified club, iff it exists."""
    current_user = request.user
    applied_club = Club.objects.get(id=club_id)
    if Membership.objects.filter(club=applied_club, user = current_user).exists():
        Membership.objects.get(club=applied_club, user=current_user).delete()
    return redirect('show_clubs')
