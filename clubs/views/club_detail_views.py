"""Views relating to viewing a club and general member facing views."""

from django.views import View

from .helpers import get_clubs_of_user
from .decorators import club_exists, membership_exists, club_exists
from django.contrib.auth.decorators import login_required
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
    return render(request, 'members_list.html', {'club': club, 'current_user': current_user , 'my_clubs':get_clubs_of_user(request.user)})

@login_required
@club_exists
def show_club(request, club_id):
    """View details of a club."""
    current_user = request.user
    club = Club.objects.get(id=club_id)
    return render(request, 'show_club.html', {'current_user': current_user, 'club': club, 'my_clubs':get_clubs_of_user(request.user)})

@login_required
@club_exists
def leave_club(request, club_id):
    """Delete the member object linking the current user to the specified club, iff it exists."""
    current_user = request.user
    applied_club = Club.objects.get(id=club_id)
    if Membership.objects.filter(club=applied_club, user = current_user).exists():
        Membership.objects.get(club=applied_club, user=current_user).delete()
    return redirect('show_clubs')
