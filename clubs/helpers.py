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
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, club_id, **kwargs)

    return modified_view_fuction

def membership_exists(view_function):
    def modified_view_fuction(request, member_id, **kwargs):
        if not Member.objects.filter(id=member_id).exists():
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, member_id, **kwargs)

    return modified_view_fuction

def application_exists(view_function):
    def modified_view_fuction(request, app_id, **kwargs):
        if not Application.objects.filter(id=app_id).exists():
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, app_id, **kwargs)

    return modified_view_fuction

def not_banned(view_function):
    def modified_view_fuction(request, club_id, **kwargs):
        club = Club.objects.get(id=club_id) #Must be used with @club_exists
        if Ban.objects.filter(club=club, user=request.user).exists():
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, club_id, **kwargs)

    return modified_view_fuction


def is_user_officer_of_club(user, club):
    return Member.objects.get(user=user, club=club).is_officer

def is_user_owner_of_club(user, club):
    return Member.objects.get(user=user, club=club).is_owner
