"""Miscellaneous views."""

from .helpers import sort_clubs, sort_clubs_for_as_set_of_clubs
from .decorators import login_prohibited, club_exists
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.utils.decorators import method_decorator


from clubs.models import Club, Application, Membership, User

from django.shortcuts import render
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from itertools import chain
from django.views import View

@login_prohibited
def home(request):
    """Generic splash page view for non-logged in user."""
    return render(request, 'home.html')


@login_required
def show_clubs(request, param=None, order=None):
    """Return a list of every club created on the website"""
    searched = None
    if request.method == "POST":
        #print(f"\n\n\n-----SEARCHED{searched}-----\n\n\n")
        searched = request.POST.get('searched')
        print(f"\n\n\n-----SEARCHED{searched}-----\n\n\n")
        clubs = Club.objects.filter(name__contains=searched)


        paginator = Paginator(clubs, settings.CLUBS_PER_PAGE)

        page = request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj  = paginator.page(1)
        except EmptyPage:
            page_obj  = paginator.page(paginator.num_pages)


        return render(request, 'club/show_clubs.html', {'searched': searched, 'current_user': request.user, 'page_obj':page_obj,})

    clubs = sort_clubs(param, order)

    paginator = Paginator(clubs, settings.CLUBS_PER_PAGE)

    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj  = paginator.page(1)
    except EmptyPage:
        page_obj  = paginator.page(paginator.num_pages)

    return render(request, 'club/show_clubs.html', {'current_user': request.user, 'searched' : searched, 'page_obj':page_obj})

class ShowClubsView(View):
    """View to show the clubs."""

    http_method_names = ['get', 'post']
    searched = None
    clubs_list = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, param, order, *args, **kwargs):
        if(self.searched):
            self.clubs_list = sort_clubs_for_as_set_of_clubs(self.clubs_list, *args, **kwargs)
        else:
            self.clubs_list = sort_clubs(param, order)

    def post(self, request):
        self.searched = request.POST.get('searched')
        self.clubs_list = Club.objects.filter(name__contains=self.searched)

    def get_clubs_list(self, clubs_list, request):
        paginator = Paginator(clubs_list, settings.CLUBS_PER_PAGE)

        page = request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj  = paginator.page(1)
        except EmptyPage:
            page_obj  = paginator.page(paginator.num_pages)

        return page_obj

    def render(self):
        return render(self.request, 'club/show_clubs.html', {'searched': self.searched, 'current_user': self.request.user, 'page_obj':self.get_clubs_list(self.clubs_list, self.request)})


@login_required
def my_clubs_list(request):
    current_user = request.user
    my_clubs = []
    for club in Club.objects.all():
        if Application.objects.filter(club=club, user=current_user):
            my_clubs.append(club)
        if Membership.objects.filter(club=club, user=current_user):
            my_clubs.append(club)

    paginator = Paginator(my_clubs, settings.CLUBS_PER_PAGE)

    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj  = paginator.page(1)
    except EmptyPage:
        page_obj  = paginator.page(paginator.num_pages)

    return render(request, 'club/my_clubs_list.html', {
        'current_user':current_user,
        'page_obj':page_obj,
    })
