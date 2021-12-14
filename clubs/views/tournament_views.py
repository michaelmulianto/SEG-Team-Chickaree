from django.http import request
from django.views import View
from django.views.generic.edit import FormView

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import OrganiseTournamentForm

from clubs.models import Tournament, Club, Organiser, Membership, Participant, GroupStage, KnockoutStage, MemberTournamentRelationship

from .decorators import club_exists, tournament_exists, user_exists, membership_exists, allowed_users
from .helpers import is_user_organiser_of_tournament, is_user_owner_of_club, is_user_officer_of_club, is_lead_organiser_of_tournament, is_participant_in_tournament


from datetime import datetime
from django.utils.timezone import now

from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404

class OrganiseTournamentView(FormView):
    """Create a new tournament."""
    form_class = OrganiseTournamentForm
    template_name = "organise_tournament.html"

    @method_decorator(login_required)
    @method_decorator(club_exists)
    @method_decorator(allowed_users(allowed_roles=[]))
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
        if Membership.objects.filter(club = self.get_context_data()['club'], user=self.request.user).exists():
            member = Membership.objects.get(user = self.request.user, club = self.get_context_data()['club'])

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
        tournament_group_stages = GroupStage.objects.filter(tournament=tournament)
        tournament_knockout_stages = list(reversed(KnockoutStage.objects.filter(tournament=tournament)))
        return render(request, 'show_tournament.html', {
                'current_user': request.user,
                'tournament': tournament,
                'tournament_group_stages': tournament_group_stages,
                'tournament_knockout_stages': tournament_knockout_stages,
            }
        )
    else:
        messages.error(request, "You are not a member of the club that organises this tournament, you can view the basic tournament details from the club's page.")
    return redirect('show_club', club_id=club.id)

@login_required
@tournament_exists
def withdraw_participation_from_tournament(request, tournament_id):
    """Have currently logged in user withdraw from a tournament, if it exists."""
    tournament = Tournament.objects.get(id=tournament_id)
    member = get_object_or_404(Membership, user = request.user, club = tournament.club)

    if Participant.objects.filter(tournament=tournament, member=member).exists():
        if tournament.deadline > now():
            Participant.objects.get(tournament=tournament, member=member).delete()
        else:
            messages.error(request, 'You cannot withdraw from the tournament as the deadline has passed.')
    else:
        messages.error(request, 'You have not participated in this tournament, ' + str(tournament.name) + '.')

    return redirect('show_club', club_id=tournament.club.id)

@login_required
@tournament_exists
def add_organisers_to_tournament(request, tournament_id, member_id):
    """Allow the head organiser of a tournament to assign other officers/owner of the club organising the tournament to officer."""

    if not Membership.objects.filter(id=member_id).exists(): #View function takes various arguments, so decorator to check for it throws an error
        messages.error(request, 'No membership with id ' + str(member_id) + ' exists.')
        return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
    else:

        tournament = Tournament.objects.get(id = tournament_id)
        new_organiser_member = Membership.objects.get(id = member_id)

        if is_lead_organiser_of_tournament(request.user, tournament):
            if not is_lead_organiser_of_tournament(new_organiser_member.user, tournament):
                if not is_participant_in_tournament(new_organiser_member.user, tournament):
                    if not is_user_organiser_of_tournament(new_organiser_member.user, tournament):
                        if is_user_owner_of_club(new_organiser_member.user, tournament.club) or is_user_officer_of_club(new_organiser_member.user, tournament.club):
                                Organiser.objects.create(
                                    member = new_organiser_member,
                                    tournament = tournament
                                )
                                messages.success(request, '@' + new_organiser_member.user.username + ' is now an organiser of the tournament: ' + tournament.name + ".")
                        else: #Access denied organiser can only assign organiser roles to other members who are officers or the owner
                            messages.error(request, 'You can only assign officers or the owner to be organisers for tournaments.')
                    else:
                        messages.warning(request, '@' + new_organiser_member.user.username + ' is already an organiser of tournament ' + tournament.name)
                else:
                    messages.warning(request, '@' + new_organiser_member.user.username + ' is already a participant of tournament ' + tournament.name)
            else:
                messages.error(request, "You are the lead organiser. You cannot add yourself as organiser.")
        else: # Access denied, member isn't the lead organiser of tournament
            messages.warning(request, 'Only the lead organiser can assign other organisers to their tournament.')

        return redirect('show_tournament', tournament_id=tournament.id)

@login_required
@tournament_exists
def join_tournament(request, tournament_id):
    tour = Tournament.objects.get(id = tournament_id)
    member = get_object_or_404(Membership, user = request.user, club = tour.club)
    is_not_organiser = Organiser.objects.filter(member = member, tournament = tour).count() == 0
    is_in_tournament = Participant.objects.filter(member = member, tournament = tour).count() > 0

    current_capacity = Participant.objects.filter(tournament = tour)
    if(current_capacity.count() < tour.capacity):
        if(is_not_organiser == True):
            if(member != None):
                if(is_in_tournament == False):
                    participant = Participant.objects.create(
                        member = member,
                        tournament = tour
                    )
                else:
                    messages.error(request, 'You are already enrolled in the tournament')
            else:
                messages.error(request, 'You are not a member of the club and cannot join the tournament')
        else:
            messages.error(request, 'You are the organizer of the tournament and are not allowed to join it')
    else:
        messages.error(request, 'Tournament is full')

    return redirect('show_club', club_id=tour.club.id)
