"""Various small views."""

from .helpers import get_clubs_of_user
from .decorators import login_prohibited, club_exists
from django.contrib.auth.decorators import login_required

from clubs.models import Club

from django.shortcuts import render

@login_prohibited
def home(request):
    """Generic splash page view for non-logged in user."""
    return render(request, 'home.html')

@login_required
def show_clubs(request):
    """Return a list of every club created on the website"""
    clubs = Club.objects.all()
    return render(request, 'show_clubs.html', {'clubs': clubs, 'current_user': request.user, 'my_clubs':get_clubs_of_user(request.user)})

@login_required
@club_exists
def manage_club(request, club_id):
    club = Club.objects.get(id=club_id)
    return render(request, 'manage_club.html', {'club': club, 'my_clubs':get_clubs_of_user(request.user)})