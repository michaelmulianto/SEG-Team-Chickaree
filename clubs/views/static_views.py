"""Various small views."""

from .helpers import login_prohibited, get_clubs_of_user
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_prohibited
def home(request):
    """Generic splash page view for non-logged in user."""
    return render(request, 'home.html')

