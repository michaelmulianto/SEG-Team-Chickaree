from django.views import View
from django.views.generic.edit import FormView

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import OrganiseTournamentForm
from clubs.models import Tournament, Club

from .decorators import club_exists, tournament_exists

from datetime import datetime
from django.utils.timezone import now

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
        if form.cleaned_data['start'] < now() or form.cleaned_data['end'] < now() or form.cleaned_data['deadline'] < now():
            messages.add_message(self.request, messages.ERROR, "Given time and date must not be in the past.")
            return super().form_invalid(form)

        desired_club = self.get_context_data()['club']
        self.object = form.save(desired_club)
        return super().form_valid(form)

    def get_success_url(self):
        club = self.get_context_data()['club']
        return reverse('show_club', kwargs={'club_id': club.id})

@login_required
@tournament_exists
def join_tournament(request,  tournament_id):  #not already in tournament
    tour = Tournmanent.objects.get(id = tournament_id)
    currentCapacity = Participant.objects.filter(tournament = tour)
    isOrganizer = True
    organizer = Organizer.objects.get(member = Membership.objects.get(user = request.user, club = tour.club), tournament = tour)
    if(organizer.count() == 0):
        isOrganizer = False

    if(tour.capacity < currentCapacity.count() and deadline < datetime.now() and isOrganizer == False):
        participant = Participant.objects.create(
            member = Membership.objects.get(user = request.user, club = tour.club),
            tournament = tour
        )
    return reverse('show_club', kwargs={'club_id': tour.club.id})
