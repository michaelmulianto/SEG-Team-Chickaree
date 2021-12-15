"""Views related to the running of a tournament"""
from django.views.generic.edit import UpdateView

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .decorators import match_exists, tournament_exists
from .helpers import is_lead_organiser_of_tournament

from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect

from clubs.forms import AddResultForm
from clubs.models import Match, Organiser, Membership, Tournament

class AddResultView(UpdateView):
    """Edit the details of the currently logged in user."""

    model = Match
    template_name = "temporary_add_result.html"
    form_class = AddResultForm

    @method_decorator(match_exists)
    @method_decorator(login_required)
    def dispatch(self, request, match_id):
        match = self.get_object()
        if match.result != 0:
            messages.add_message(self.request, messages.ERROR, "The match has already had the result registered!")
            return redirect('show_clubs')

        # We must verify permissions...
        t = match.collection.tournament

        if not Membership.objects.filter(club=t.club,user=request.user).exists():
            messages.add_message(self.request, messages.ERROR, "The tournament is for members only!")
            return redirect('show_clubs')

        member = Membership.objects.get(club=t.club,user=request.user)

        if not Organiser.objects.filter(tournament=t, member=member).exists():
            messages.add_message(self.request, messages.ERROR, "Only organisers can set match results!")
            return redirect('show_clubs')

        return super().dispatch(request)

    def get_form(self):
        my_form = super().get_form()
        try:
            self.get_object().collection.tournamentstagebase.knockoutstage
        except:
            # Not knockoutstage: do nothing
            pass
        else:
            my_form.fields["result"].choices = my_form.fields["result"].choices[:2]
        return my_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.request.user
        return context

    def get_object(self):
        """Return the object (match) to be updated."""
        return Match.objects.get(id=self.kwargs['match_id'])

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Result Registered!")
        return reverse('show_clubs')


@login_required
@tournament_exists
def add_tournament_organiser_list(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    club = tournament.club
    if Membership.objects.filter(user=request.user, club=club).exists():
        member =  Membership.objects.get(user=request.user, club=club)
        if is_lead_organiser_of_tournament(request.user, tournament): # Every tournament must have a lead organiser (and therefore an organiser)
            return render(request, 'add_tournament_organiser_list.html', {
                    'current_user': request.user,
                    'tournament': tournament
                }
            )
        else:
            messages.error(request, "Only the lead organiser can access add organisers.")
    else:
        messages.error(request, "You are not a member of the club that organises this tournament, you can view the basic tournament details from the club's page.")
        return redirect('show_club', club_id=club.id)
    return redirect('show_tournament', tournament_id=tournament.id)

@login_required
@tournament_exists
def add_organiser_to_tournament(request, tournament_id, member_id):
    """Allow the head organiser of a tournament to assign other officers/owner of the club organising the tournament to officer."""

    if not Membership.objects.filter(id=member_id).exists(): #View function takes various arguments, so decorator to check for it throws an error
        messages.error(request, 'No membership with id ' + str(member_id) + ' exists.')
        return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
    else:

        tournament = Tournament.objects.get(id = tournament_id)
        new_organiser_member = Membership.objects.get(id = member_id)

        if is_lead_organiser_of_tournament(request.user, tournament):
            if not is_user_organiser_of_tournament(new_organiser_member.user, tournament):
                if not is_participant_in_tournament(new_organiser_member.user, tournament):
                    if is_user_owner_of_club(new_organiser_member.user, tournament.club) or is_user_officer_of_club(new_organiser_member.user, tournament.club):
                        Organiser.objects.create(
                            member = new_organiser_member,
                            tournament = tournament
                        )
                        messages.success(request, '@' + new_organiser_member.user.username + ' is now an organiser of the tournament: ' + tournament.name + ".")
                    else: #Access denied organiser can only assign organiser roles to other members who are officers or the owner
                        messages.error(request, 'You can only assign officers or the owner to be organisers for tournaments.')
                else: # User is a participant, so they cannot be an organiser of the same tournament
                    messages.warning(request, '@' + new_organiser_member.user.username + ' is already a participant of tournament ' + tournament.name)
            else: # User is already an organiser
                if is_user_organiser_of_tournament(new_organiser_member.user, tournament):
                    messages.error(request, "You are the lead organiser. You cannot add yourself as organiser.")
                else:
                    messages.warning(request, '@' + new_organiser_member.user.username + ' is already an organiser of tournament ' + tournament.name)
        else: # Access denied, member isn't the lead organiser of tournament
            messages.warning(request, 'Only the lead organiser can assign other organisers to their tournament.')

        return redirect('show_tournament', tournament_id=tournament.id)
