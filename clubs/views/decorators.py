"""Decorators representing requirements of views to be accessed"""

from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings
from clubs.models import Organiser, User, Club, Membership, Application, Ban, Tournament
from django.http import HttpResponse

def login_prohibited(view_function):
    def modified_view_fuction(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)

    return modified_view_fuction

def user_exists(view_function):
    def modified_view_fuction(request, user_id, **kwargs):
        if not User.objects.filter(id=user_id).exists():
            messages.error(request, 'No user with id ' + str(user_id) + ' exists.')
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, user_id, **kwargs)

    return modified_view_fuction

def club_exists(view_function):
    def modified_view_fuction(request, club_id, **kwargs):
        if not Club.objects.filter(id=club_id).exists():
            messages.error(request, 'No club with id ' + str(club_id) + ' exists.')
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, club_id, **kwargs)

    return modified_view_fuction

def tournament_exists(view_function):
    def modified_view_fuction(request, tournament_id, **kwargs):
        if not Tournament.objects.filter(id=tournament_id).exists():
            messages.error(request, 'No tournament with id ' + str(tournament_id) + ' exists.')
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, tournament_id, **kwargs)

    return modified_view_fuction

def membership_exists(view_function):
    def modified_view_fuction(request, member_id, **kwargs):
        if not Membership.objects.filter(id=member_id).exists():
            messages.error(request, 'No membership with id ' + str(member_id) + ' exists.')
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, member_id, **kwargs)

    return modified_view_fuction

def application_exists(view_function):
    def modified_view_fuction(request, app_id, **kwargs):
        if not Application.objects.filter(id=app_id).exists():
            messages.error(request, 'No application with id ' + str(app_id) + ' exists.')
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, app_id, **kwargs)

    return modified_view_fuction

def ban_exists(view_function):
    def modified_view_fuction(request, ban_id, **kwargs):
        if not Ban.objects.filter(id=ban_id).exists():
            messages.error(request, 'No ban with id ' + str(ban_id) + ' exists.')
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, ban_id, **kwargs)

    return modified_view_fuction

def tournament_exists(view_function):
    def modified_view_fuction(request, tournament_id, **kwargs):
        if not Tournament.objects.filter(id=tournament_id).exists():
            messages.error(request, 'No tournament with id ' + str(tournament_id) + ' exists.')
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, tournament_id, **kwargs)

    return modified_view_fuction

def not_banned(view_function):
    def modified_view_fuction(request, club_id, **kwargs):
        club = Club.objects.get(id=club_id) #Must be used with @club_exists
        if Ban.objects.filter(club=club, user=request.user).exists():
            member = Membership.objects.get(club=club, is_owner=True)
            messages.error(request, 'You are banned from ' + club.name + '. Contact the owner ' + member.user.first_name + ' ' + member.user.last_name + ' for details by email at ' + member.user.email + '.')
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, club_id, **kwargs)

    return modified_view_fuction

def is_head_organiser(view_function):
    def modified_view_function(request, tournament_id, membership_id, **kwargs):
        tournament = Tournament.objects.get(id=tournament_id) #Must be used is @tournament_exists
        member = Membership.objects.get(id=membership_id) #Must be used with @membership_exists
        if not Organiser.objects.filter(tournament = tournament, member = member, is_head_organiser = True).exists():
            messages.error(request, 'The membership with id ' + str(membership_id) + ' for tournament ' + str(tournament_id) + " exists.")
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, tournament_id, membership_id, **kwargs)

    return modified_view_function

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, club_id, **kwargs):
            club = Club.objects.get(id=club_id)
            member = Membership.objects.get(user = request.user, club = club)
            group = None
            if member.is_owner == True or member.is_officer == True:
                group = True
            if group == True:
                return view_func(request, club_id, **kwargs)
            else:
                return HttpResponse('You are not authorized to view this page')

        return wrapper_func
    return decorator
