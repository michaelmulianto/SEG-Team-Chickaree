from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings
from clubs.models import User, Club, Member, Application, Ban

def login_prohibited(view_function):
    def modified_view_fuction(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)

    return modified_view_fuction

def club_exists(view_function):
    def modified_view_fuction(request, club_id, **kwargs):
        if not Club.objects.filter(id=club_id).exists():
            messages.error(request, 'No club with id ' + str(club_id) + ' exists.')
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, club_id, **kwargs)

    return modified_view_fuction

def membership_exists(view_function):
    def modified_view_fuction(request, member_id, **kwargs):
        if not Member.objects.filter(id=member_id).exists():
            messages.error(request, 'No user with membership id ' + str(member_id) + ' exists.')
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, member_id, **kwargs)

    return modified_view_fuction

def application_exists(view_function):
    def modified_view_fuction(request, app_id, **kwargs):
        if not Application.objects.filter(id=app_id).exists():
            messages.error(request, 'No user with application id ' + str(app_id) + ' exists.')
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, app_id, **kwargs)

    return modified_view_fuction

def ban_exists(view_function):
    def modified_view_fuction(request, ban_id, **kwargs):
        if not Ban.objects.filter(id=ban_id).exists():
            messages.error(request, 'No user with ban id ' + str(ban_id) + ' exists.')
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, ban_id, **kwargs)

    return modified_view_fuction

def not_banned(view_function):
    def modified_view_fuction(request, club_id, **kwargs):
        club = Club.objects.get(id=club_id) #Must be used with @club_exists
        if Ban.objects.filter(club=club, user=request.user).exists():
            member = Member.objects.get(club=club, is_owner=True)
            messages.error(request, 'You are banned from ' + club.name + '. Contact the owner ' + member.user.first_name + ' ' + member.user.last_name + ' for details by email at ' + member.user.email + '.')
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, club_id, **kwargs)

    return modified_view_fuction


def is_user_officer_of_club(user, club):
    return Member.objects.get(user=user, club=club).is_officer

def is_user_owner_of_club(user, club):
    return Member.objects.get(user=user, club=club).is_owner
