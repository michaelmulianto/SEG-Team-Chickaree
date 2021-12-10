from django.views import View
from django.views.generic.edit import FormView

from .decorators import login_prohibited
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import OrganiseTournamentForm
from clubs.models import Tournament, Club

from .decorators import club_exists

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
        context['club'] = Club.objects.get(id=self.kwargs['club_id'])
        return context

    def form_valid(self, form):
        desired_club = self.get_context_data()['club']
        self.object = form.save(desired_club)
        return super().form_valid(form)

    def get_success_url(self):
        club = self.get_context_data()['club']
        return reverse('show_club', kwargs={'club_id': club.id})

@login_required
@membership_exists
@tournament_exists
def join_tournament(request,  tournament_id): #before deadline, not organizer, not already in tournament, add decorator for tournament
    tour = Tournmanent.objects.get(id = tournament_id)
    currentCapacity = MemberTournamentRelationship.objects.filter(tournament = tour)
    if(tour.capacity < currentCapacity.count()):
        participant = Participant.objects.create(
            member = Membership.objects.get(user = request.user, club = tour.club)
            tournament = tour
        )
    return render
