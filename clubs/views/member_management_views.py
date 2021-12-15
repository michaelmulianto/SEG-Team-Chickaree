"""Views relating to club members."""

from django.views import View
from django.contrib import messages
from django.shortcuts import render, redirect

from .helpers import is_user_owner_of_club, is_user_officer_of_club
from .decorators import membership_exists, ban_exists, club_exists
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.models import Membership, Club, Ban

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.conf import settings


@login_required
@membership_exists
def kick_member(request, member_id):
    """Allow an owner or officer to kick a given member from their club."""
    current_user = request.user
    member = Membership.objects.get(id=member_id)
    club = member.club
    if is_user_owner_of_club(current_user, club) or is_user_officer_of_club(current_user, club):
        if not is_user_officer_of_club(member.user, club):
            if not is_user_owner_of_club(member.user, club):
                Membership.objects.filter(id=member_id).delete()
                messages.warning(request, '@' + member.user.username + ' was kicked from the club.')
            else:
                messages.error(request, 'You are the owner. You cannot kick yourself from your club. Transfer ownership before leaving or delete the club.')
        else:
            messages.error(request, 'You cannot kick a officer, demote them first (owner only).')
    else:
        messages.error(request, 'Only the owners and officers can kick members from a club.')
    return redirect('members_list', club_id=club.id)

@login_required
@membership_exists
def ban_member(request, member_id):
    """Allow the owner to ban a given member from their club."""
    current_user = request.user
    member = Membership.objects.get(id=member_id)
    club = member.club
    if is_user_owner_of_club(current_user, club):
        if not is_user_officer_of_club(member.user, club): #Owners can only ban members, not officers.
            if not is_user_owner_of_club(member.user, club): #An owner cannot ban themselves.
                Ban.objects.create(club=club, user=member.user)
                Membership.objects.filter(id=member_id).delete()
                messages.warning(request, '@' + member.user.username + ' was banned from the club.')
            else:
                messages.error(request, "You are the owner. You cannot ban yourself from your club.")
        else: #Tried to ban an officer.
            messages.error(request, 'You cannot ban an officer. Demote them first.')
    else: #Not the owner
        messages.error(request, 'Only the owner can ban members of a club.')
    return redirect('members_list', club_id=club.id)


@login_required
@club_exists
def banned_members(request, club_id):
    """Allow the owner and officer of a club to view banned members to said club."""
    club_to_view = Club.objects.get(id = club_id)
    if is_user_owner_of_club(request.user, club_to_view) or is_user_officer_of_club(request.user, club_to_view):

        paginator = Paginator(club_to_view.get_banned_members(), settings.BANNED_MEMBERS_PER_PAGE)

        page = request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj  = paginator.page(1)
        except EmptyPage:
            page_obj  = paginator.page(paginator.num_pages)

        return render(request, 'club/banned_member_list.html', {'current_user': request.user, 'club': club_to_view, 'banned_members':page_obj})
    else: #Access denied
        messages.error(request, "Only the club owner and officers can view banned members")
        return redirect('show_club', club_id=club_id)


@login_required
@ban_exists
def unban_member(request, ban_id):
    """Allow the owner to revoke a given ban from their club."""
    current_user = request.user
    ban = Ban.objects.get(id=ban_id)
    club = ban.club
    if is_user_owner_of_club(current_user, club):
        Membership.objects.create(club=club, user=ban.user)
        Ban.objects.filter(id=ban_id).delete()
        messages.warning(request, '@' + ban.user.username + ' was unban from the club.')
    else:
        messages.error(request, 'Only the owner can unban members.')

    return redirect('banned_members', club_id=club.id)

@login_required
@membership_exists
def promote_member_to_officer(request, member_id):
    """Allow the owner of a club to promote some member of said club to officer."""
    member = Membership.objects.get(id = member_id)
    club = member.club
    if is_user_owner_of_club(request.user, club):
        if not is_user_owner_of_club(member.user, club):
            if not is_user_officer_of_club(member.user, club):
                member.is_officer = True
                member.save() # Or database won't update.
                messages.success(request, '@' + member.user.username + ' was promoted to officer.')
            else: #Access denied owner is trying to promote an officer.
                messages.warning(request, '@' + member.user.username + ' is already an officer.')
        else: #Access denied owner is trying to promote themselves.
            messages.error(request, 'You are the owner. You cannot promote yourself to officer.')
    else: # Access denied, member isn't owner.
        messages.error(request, 'Only the owner can promote members.')

    return redirect('members_list', club_id=club.id)

@login_required
@membership_exists
def demote_officer_to_member(request, member_id):
    """Allow the owner of a club to promote some member of said club to officer."""
    member = Membership.objects.get(id = member_id)
    club = member.club
    if is_user_owner_of_club(request.user, club) :
        if not is_user_owner_of_club(member.user, club):
            if is_user_officer_of_club(member.user, club):
                member.is_officer = False
                member.save() # Or database won't update.
                messages.warning(request, '@' + member.user.username + ' was demoted.')
            else: #Access denied, trying to demote non-officer.
                messages.warning(request, '@' + member.user.username + ' is not an officer.')
        else: #Access denied, owner is trying to demote themselves.
            messages.error(request, 'You are the owner. You cannot demote yourself. You can transfer ownership from the member list.')
    else: # Access denied, member isn't owner
        messages.error(request, 'Only the owner can demote members.')

    return redirect('members_list', club_id=club.id)
