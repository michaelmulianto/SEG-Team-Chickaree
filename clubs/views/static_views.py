"""Miscellaneous views."""

from .helpers import get_clubs_of_user
from .decorators import login_prohibited, club_exists
from django.contrib.auth.decorators import login_required

from clubs.models import Club, Application, Member

from django.shortcuts import render
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator    

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

    return render(request, 'my_clubs_list.html', {
        'clubs': my_clubs, 
        'current_user':current_user, 
        'page_obj':page_obj, 
        'my_clubs':get_clubs_of_user(request.user)
    })