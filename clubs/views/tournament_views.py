from django.http import request
from django.views import View
from django.views.generic.edit import FormView

from .decorators import login_prohibited, user_exists
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import OrganiseTournamentForm
from clubs.models import Tournament, Club, Organiser, Membership

from .decorators import club_exists
from .helpers import is_user_owner_of_club, is_user_officer_of_club

from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect

class OrganiseTournamentView(FormView):
    """Create a new tournament."""
    form_class = OrganiseTournamentForm
    template_name = "organise_tournament.html"

    @method_decorator(login_required)
    @method_decorator(club_exists)
    def dispatch(self, request, club_id):
        return super().dispatch(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.request.user
        context['club'] = Club.objects.get(id=self.kwargs['club_id'])
        return context

    def form_valid(self, form):
        self.object = form.save()
        club = Club.objects.get(id=self.kwargs['club_id'])

        if is_user_owner_of_club(request.user, club):
            pass

        member = Membership.objects.get(user = self.request.user, 
                                        club = club)

        Organiser.objects.create(
            member = member,
            tournament = new_tournament,
            is_lead_organiser = True
        )
        return super().form_valid(form)


    def form_valid(self, form):
        desired_club = self.get_context_data()['club']
        self.object = form.save(desired_club)
        return super().form_valid(form)

    def get_success_url(self):
        club = self.get_context_data()['club']
        return reverse('show_club', kwargs={'club_id': club.id})

    
    @method_decorator(user_exists)
    def create_organiser(self, user):
        pass


