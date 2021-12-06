"""Views relating to viewing a club and general member facing views."""

from django.views import View

from .helpers import get_clubs_of_user
from .decorators import club_exists, membership_exists, club_exists
from django.contrib.auth.decorators import login_required
# from django.utils.decorators import method_decorator

from clubs.models import Member, Club

from django.shortcuts import render, redirect

@login_required
@club_exists
def members_list(request, club_id):
    """Display a list of the members in a club"""
    current_user = request.user
    club = Club.objects.get(id = club_id)
    members = Member.objects.filter(club = club)
    return render(request, 'members_list.html', {'members': members, 'club': club, 'current_user': current_user , 'my_clubs':get_clubs_of_user(request.user)})


@login_required
@club_exists
def show_club(request, club_id):
    """View details of a club."""
    current_user = request.user
    club = Club.objects.get(id=club_id)
    members = Member.objects.filter(club = club)
    officers = members.filter(is_officer = True)
    officer_count = officers.count()
    get_owner = members.get(is_owner = True)
    num_members = members.count()
    check_user_is_member = members.filter(user = current_user)
    is_member = False
    is_owner = False
    is_officer = False
    if check_user_is_member.filter(is_owner = True).count() > 0:
        is_owner = True
    if check_user_is_member.count() > 0:
        is_member = True
    if check_user_is_member.filter(is_officer = True).count() > 0:
        is_officer = True
    return render(request, 'show_club.html', {'club': club, 'members': num_members, 'userIsMember': is_member, 'owner': get_owner, 'userIsOwner': is_owner, 'userIsOfficer': is_officer, 'officers': officers, 'officerCount': officer_count, 'my_clubs':get_clubs_of_user(request.user)})


@login_required
@club_exists
def leave_club(request, club_id):
    """Delete the member object linking the current user to the specified club, iff it exists."""
    current_user = request.user
    applied_club = Club.objects.get(id=club_id)
    if Member.objects.filter(club=applied_club, user = current_user).exists():
        Member.objects.get(club=applied_club, user=current_user).delete()
    return redirect('show_clubs')