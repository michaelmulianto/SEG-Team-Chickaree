from .helpers import login_prohibited
from django.shortcuts import render

@login_prohibited
def home(request):
    """Generic splash page view for non-logged in user."""
    return render(request, 'home.html')