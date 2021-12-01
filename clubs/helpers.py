from django.shortcuts import redirect
from django.conf import settings
from clubs.models import User, Club, Member

def login_prohibited(view_function):
    def modified_view_fuction(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)

    return modified_view_fuction

def is_user_officer_of_club(user, club):
    return Member.objects.get(user=user, club=club).is_officer

def is_user_owner_of_club(user, club):
    return Member.objects.get(user=user, club=club).is_owner
