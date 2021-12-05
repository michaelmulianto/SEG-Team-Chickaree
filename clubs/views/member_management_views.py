"""Views relating to club applications."""

from django.views import View

from .helpers import is_user_owner_of_club, is_user_officer_of_club, get_clubs_of_user
from .decorators import membership_exists, ban_exists
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.models import Member, Club, Ban

from django.contrib import messages
from django.shortcuts import render, redirect

@login_required
@membership_exists
def kick_member(request, member_id):
    current_user = request.user
    member = Member.objects.get(id=member_id)
    club = member.club
    if is_user_owner_of_club(current_user, club) or is_user_officer_of_club(current_user, club):
        Member.objects.filter(id=member_id).delete()
    return redirect('members_list', club_id=club.id)

@login_required
@membership_exists
def ban_member(request, member_id):
    current_user = request.user
    member = Member.objects.get(id=member_id)
    club = member.club
    if is_user_owner_of_club(current_user, club) and not is_user_officer_of_club(member.user, club): #Only owners can ban members, not officers.
        Ban.objects.create(club=club, user=member.user)
        Member.objects.filter(id=member_id).delete()
    return redirect('members_list', club_id=club.id)

@login_required
@ban_exists
def unban_member(request, ban_id):
    current_user = request.user
    ban = Ban.objects.get(id=ban_id)
    club = ban.club
    if is_user_owner_of_club(current_user, club):
        Member.objects.create(club=club, user=ban.user)
        Ban.objects.filter(id=ban_id).delete()
    else:
        member = Member.objects.get(club=club, is_owner=True)
        messages.error(request, 'Only the owner can unban users. Please ask ' + member.user.first_name + ' ' + member.user.last_name + ' to perform this action for you.')
    return redirect('members_list', club_id=club.id)

@login_required
@membership_exists
def promote_member_to_officer(request, member_id):
    """Allow the owner of a club to promote some member of said club to officer."""
    member = Member.objects.get(id = member_id)
    club = member.club
    if not(is_user_owner_of_club(request.user, club)):
        # Access denied, member isn't owner
        return redirect('show_clubs')

    member.is_officer = True
    member.save() # Or database won't update.
    return redirect('members_list', club_id=club.id)

@login_required
@membership_exists
def demote_officer_to_member(request, member_id):
    """Allow the owner of a club to promote some member of said club to officer."""
    member = Member.objects.get(id = member_id)
    club = member.club
    if not(is_user_owner_of_club(request.user, club)):
        # Access denied, member isn't owner
        return redirect('show_clubs')

    member.is_officer = False
    member.save() # Or database won't update.
    return redirect('members_list', club_id=club.id)