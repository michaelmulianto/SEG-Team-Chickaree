from .helpers import login_prohibited
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_prohibited
def home(request):
    """Generic splash page view for non-logged in user."""
    return render(request, 'home.html')

@login_required
def account(request):
    """Render a page displaying the attributes of the currently logged in user."""
    return render(request, 'account.html', {'user': request.user, 'my_clubs':get_clubs_of_user(request.user)})