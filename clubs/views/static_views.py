"""Miscellaneous views."""

from .helpers import sort_clubs
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

@login_prohibited
def home(request):
    """Generic splash page view for non-logged in user."""
    return render(request, 'home.html')


@login_required
def show_clubs(request, param=None, order=None):
    """Return a list of every club created on the website"""
    if request.method == "POST":
        searched = request.POST.get('searched')
        clubs = Club.objects.filter(name__contains=searched)

        paginator = Paginator(clubs, settings.CLUBS_PER_PAGE)

        page_number = request.GET.get('page')

        page_obj  = paginator.get_page(page_number)


        return render(request, 'show_clubs.html', {'searched': searched, 'current_user': request.user, 'clubs': clubs, 'page_obj':page_obj,})
    clubs = sort_clubs(param, order)

    paginator = Paginator(clubs, settings.CLUBS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj  = paginator.get_page(page_number)

    return render(request, 'show_clubs.html', {'current_user': request.user, 'clubs': clubs, 'order': order, 'page_obj':page_obj})

# class ShowClubsView(LoginRequiredMixin, ListView):
#     model = Club
#     template_name = "show_clubs.html"
#     context_object_name = "clubs"
#     paginate_by = settings.CLUBS_PER_PAGE
#     searched = None
#     param = None
#     order = None


#     @method_decorator(login_required)
#     def dispatch(self, request, *args,**kwargs):
#         return super().dispatch(request, *args, **kwargs)

#     def get_context_data(self, *args, **kwargs):
#         """Generate content to be displayed in the template"""

#         context = super().get_context_data(*args, **kwargs)
#         user = self.get_object()
#         context['searched'] = self.searched
#         context['current_user'] = user
#         context['clubs'] = sort_clubs(self.param, self.order)
#         context['order'] = self.order
#         return context

#     def get_object(self):
#         return User.objects.filter(id = self.request.user.id)


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

    return render(request, 'my_clubs_list.html', {
        'clubs': my_clubs, 
        'current_user':current_user, 
        'page_obj':page_obj, 
    })

# class MyClubsListView(LoginRequiredMixin, ListView):
#     """View that shows a list of all club a user is a part of"""

#     model = Club
#     template_name = "my_clubs_list.html"
#     context_object_name = "clubs"
#     paginate_by = settings.CLUBS_PER_PAGE

#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispath(request, *args, **kwargs)

#     def get_context_data(self, *args, **kwargs):

#         context =  super().get_context_data(*args, **kwargs)
#         current_user = self.get_object()
#         context['clubs'] = self.get_membership_and_applications(current_user)
#         context['current_user'] = current_user

#     def get_object(self):
#         return User.objects.filter(id = self.request.user.id)

#     def get_membership_and_applications(self, current_user):
#         application_queryset = None
#         membership_queryset = None
#         for club in Club.objects.all():
#             if Application.objects.filter(club=club, user=current_user):
#                 list(chain(application_queryset, Application.objects.filter(club=club, user=current_user)))
#             if Membership.objects.filter(user=current_user):
#                 list(chain(membership_queryset, Membership.objects.filter(club=club, user=current_user)))

#         memberships_and_applications = list(chain(application_queryset, membership_queryset))
#         return memberships_and_applications


    
