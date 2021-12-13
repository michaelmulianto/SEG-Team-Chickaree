from django.views import View
from django.views.generic.edit import FormView

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import OrganiseTournamentForm
from clubs.models import Membership, Tournament, Club, Organiser, Participant, MemberTournamentRelationship

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
def show_tournament(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    club = tournament.club
    if Membership.objects.filter(user=request.user, club=club):
        return render(request, 'show_tournament.html', { 'current_user': request.user, 'tournament': tournament })
    else:
        messages.error(request, "You are not a member of the club that organises this tournament, you can view the basic tournament details from the club's page.")
    return redirect('show_club', club_id=club.id)

@login_required
@tournament_exists
def join_tournament(request, tournament_id):
    tour = Tournament.objects.get(id = tournament_id)
    member = Membership.objects.get(user = request.user, club = tour.club)
    is_organiser = True
    organiser = Organiser.objects.filter(member = member, tournament = tour)
    if(organiser.count() == 0):
        is_organiser = False

    is_member = True
    if(member != None):
        is_member = False

    is_in_tournament = False
    check_tournament = Participant.objects.filter(member = member, tournament = tour)
    if(check_tournament.count() > 0):
        is_in_tournament = True

    currentCapacity = Participant.objects.filter(tournament = tour)
    if(tour.capacity < currentCapacity.count() and deadline < datetime.now() and is_organiser == False and is_member == True and is_in_tournament == False):
        participant = Participant.objects.create(
            member = member,
            tournament = tour
        )

    return redirect('show_club', club_id=tour.club.id)
