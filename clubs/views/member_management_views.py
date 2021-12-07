"""Views relating to club members."""

from django.views import View

from .helpers import is_user_owner_of_club, is_user_officer_of_club, get_clubs_of_user
from .decorators import membership_exists, ban_exists, club_exists
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.models import Membership, Club, Ban

from django.contrib import messages
from django.shortcuts import render, redirect

@login_required
@membership_exists
def kick_member(request, member_id):
    """Kick a given member from their club."""
    current_user = request.user
    member = Membership.objects.get(id=member_id)
    club = member.club
    if is_user_owner_of_club(current_user, club) or is_user_officer_of_club(current_user, club):
        Membership.objects.filter(id=member_id).delete()
    return redirect('members_list', club_id=club.id)

@login_required
@membership_exists
def ban_member(request, member_id):
    """Ban a given member from their club."""
    current_user = request.user
    member = Membership.objects.get(id=member_id)
    club = member.club
    if is_user_owner_of_club(current_user, club) and not is_user_officer_of_club(member.user, club): #Only owners can ban members, not officers.
        Ban.objects.create(club=club, user=member.user)
        Membership.objects.filter(id=member_id).delete()
        messages.warning(request, '@' + member.user.username + ' was banned from the club.')
    elif not is_user_owner_of_club(current_user, club):
        messsages.error(request, 'Only the owner can ban members of a club.')
    else is_user_officer_of_club(member.user, club):
        messages.error(request, 'You cannot ban an officer. Demote them first.')
    return redirect('members_list', club_id=club.id)


@login_required
@club_exists
def banned_members(request, club_id):
    """Allow the owner of a club to view all applications to said club."""
    club_to_view = Club.objects.get(id = club_id)
    if not is_user_owner_of_club(request.user, club_to_view):
        # Access denied
        messages.error(request, "Only the club owner can view banned members")
        return redirect('show_clubs')

    banned_members = Ban.objects.filter(club = club_to_view)
    return render(request, 'banned_member_list.html', {'club': club_to_view, 'banned_members': banned_members, 'my_clubs':get_clubs_of_user(request.user)})


@login_required
@ban_exists
def unban_member(request, ban_id):
    """Revoke a given ban from their club."""
    current_user = request.user
    ban = Ban.objects.get(id=ban_id)
    club = ban.club
    if is_user_owner_of_club(current_user, club):
        Membership.objects.create(club=club, user=ban.user)
        Ban.objects.filter(id=ban_id).delete()
    else:
        member = Membership.objects.get(club=club, is_owner=True)
        messages.error(request, 'Only the owner can unban users. Please ask ' + member.user.first_name + ' ' + member.user.last_name + ' to perform this action for you.')
    return redirect('members_list', club_id=club.id)

@login_required
@membership_exists
def promote_member_to_officer(request, member_id):
    """Allow the owner of a club to promote some member of said club to officer."""
    member = Membership.objects.get(id = member_id)
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
    member = Membership.objects.get(id = member_id)
    club = member.club
    if not(is_user_owner_of_club(request.user, club)):
        # Access denied, member isn't owner
        return redirect('show_clubs')

    member.is_officer = False
    member.save() # Or database won't update.
    return redirect('members_list', club_id=club.id)
