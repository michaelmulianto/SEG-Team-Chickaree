from django.views import View
from django.views.generic.edit import FormView

from .decorators import login_prohibited, tournament_exists
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import OrganiseTournamentForm
from clubs.models import Membership, Tournament, Club

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
        context['current_user'] = self.request.user
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
@tournament_exists
def show_tournament(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    club = tournament.club
    if Membership.objects.filter(user=request.user, club=club):
        tournament_group_stages = tournament.get_group_stages()
        return render(request, 'show_tournament.html', {
                'current_user': request.user,
                'tournament': tournament,
                'tournament_group_stages': tournament_group_stages
            }
        )
    else:
        messages.error(request, "You are not a member of the club that organises this tournament, you can view the basic tournament details from the club's page.")
    return redirect('show_club', club_id=club.id)
