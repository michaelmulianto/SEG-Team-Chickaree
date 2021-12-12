from django.http import request
from django.views import View
from django.views.generic.edit import FormView

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import OrganiseTournamentForm
from clubs.models import Tournament, Club, Organiser, Membership

from .decorators import club_exists, is_head_organiser, membership_exists, tournament_exists, user_exists
from .helpers import is_user_owner_of_club, is_user_officer_of_club

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
        if not is_user_owner_of_club(self.request.user, self.get_context_data()['club']) and not is_user_officer_of_club(self.request.user, self.get_context_data()['club']):
            messages.add_message(self.request, messages.ERROR, "Only Owners or Officers of a club can create tournaments")
            return super().form_invalid(form)

        if form.cleaned_data['start'] < now() or form.cleaned_data['end'] < now() or form.cleaned_data['deadline'] < now():
            messages.add_message(self.request, messages.ERROR, "Given time and date must not be in the past.")
            return super().form_invalid(form)

        self.object = form.save(self.get_context_data()['club'])
        member = Membership.objects.get(user = self.request.user, 
                                    club = self.get_context_data()['club'])

        Organiser.objects.create(
            member = member,
            tournament = self.object,
            is_lead_organiser = True
        )
        return super().form_valid(form)
            

    def get_success_url(self):
        club = self.get_context_data()['club']
        return reverse('show_club', kwargs={'club_id': club.id})
    
    @method_decorator(user_exists)
    def create_organiser(self, user):
        pass


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

@user_exists
@login_required
@membership_exists
@tournament_exists
def add_organisers_to_tournament(request, tournament_id, member_id):
    """Allow the head organiser of a tournament to assign other officers/owner of the club organising the tournament to officer."""
    tournament = Tournament.objects.get(id = tournament_id)
    new_organiser_member = Membership.objects.get(id = member_id)

    if is_head_organiser(request.user, tournament):
        if is_user_owner_of_club(new_organiser_member.user, tournament.club) or is_user_officer_of_club(new_organiser_member.user, tournament.club):
                Organiser.objects.create(
                    member = new_organiser_member,
                    tournament = tournament
                )
                messages.success(request, '@' + new_organiser_member.user.username + ' is now an organiser of the tournament: ' + tournament.name + ".")
        else: #Access denied organiser can only assign organiser roles to other members who are officers or the owner
            messages.error(request, 'You can only assign officers or the owner to be ')
    else: # Access denied, member isn't the lead organiser of tournament
        messages.error(request, 'Only the lead organiser can assign other organisers to their tournament.')

    return redirect('show_tournament', club_id=tournament.club.id)
