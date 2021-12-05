"""
Define the views for the system.

"""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from clubs import forms
from django.http import HttpResponseForbidden, request
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.conf import settings
from clubs.forms import LogInForm, SignUpForm, CreateClubForm, EditAccountForm, ApplyToClubForm, EditClubInfoForm
from clubs.models import User, Club, Application, Member, Ban
from .decorators import login_prohibited, club_exists, application_exists, membership_exists, ban_exists, not_banned
from .helpers import is_user_officer_of_club, is_user_owner_of_club, get_clubs_of_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views import View
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator    

@login_required
def my_clubs_list(request):
    current_user = request.user
    my_clubs = []
    for club in Club.objects.all():
        if Application.objects.filter(club=club, user=current_user):
            my_clubs.append(club)
        if Member.objects.filter(club=club, user=current_user):
            my_clubs.append(club)

    paginator = Paginator(my_clubs, settings.CLUBS_PER_PAGE)

    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj  = paginator.page(1)
    except EmptyPage:
        page_obj  = paginator.page(paginator.num_pages)

    return render(request, 'my_clubs_list.html', {'clubs': my_clubs, 'current_user':current_user, 'page_obj':page_obj, 'my_clubs':get_clubs_of_user(request.user)})


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
    if not(Member.objects.filter(club=club, user=request.user, is_owner=True).exists()):
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
    if not(Member.objects.filter(club=club, user=request.user, is_owner=True).exists()):
        # Access denied, member isn't owner
        return redirect('show_clubs')
    member.is_officer = False
    member.save() # Or database won't update.
    return redirect('members_list', club_id=club.id)

