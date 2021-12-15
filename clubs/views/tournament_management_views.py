"""Views related to the running of a tournament"""
from django.views.generic.edit import UpdateView

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .decorators import match_exists, tournament_exists
from .helpers import is_user_organiser_of_tournament, is_user_member_of_club

from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect

from clubs.forms import AddResultForm
from clubs.models import Match, Tournament, Membership

@login_required
@tournament_exists
def begin_tournament(request, tournament_id):
    """View to begin a tournament."""
    tournament = Tournament.objects.get(id=tournament_id)
    if not is_user_member_of_club(request.user, tournament.club):
        messages.add_message(request, messages.ERROR, "The tournament is for members only!")
        return redirect('show_clubs')
        
    elif not is_user_organiser_of_tournament(request.user, tournament):
        messages.add_message(request, messages.ERROR, "Only organisers can begin the tournament!")
        
    elif tournament.get_current_round() != None:
        messages.add_message(request, messages.ERROR, "The tournament has already begun!")
        
    else:
        tournament.generate_next_round()
        messages.add_message(request, messages.SUCCESS, "Tournament begun!")
        
    return redirect('show_tournament', tournament_id= tournament_id)

class AddResultView(UpdateView):
    """Edit the result of a match, if result not already set."""

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

        if not is_user_member_of_club(request.user, t.club):
            messages.add_message(self.request, messages.ERROR, "The tournament is for members only!")
            return redirect('show_clubs')
            
        if not is_user_organiser_of_tournament(self.request.user, t):
            messages.add_message(self.request, messages.ERROR, "Only organisers can set match results!")
            return redirect('show_clubs')

        return super().dispatch(request)

    def get_form(self):
        my_form = super().get_form()
        try:
            match.collection.tournamentstagebase.knockoutstage
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