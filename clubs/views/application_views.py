"""Views relating to club applications."""

from django.views import View
from django.views.generic.edit import FormView

from .helpers import get_clubs_of_user
from .decorators import club_exists, membership_exists, not_banned
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import ApplyToClubForm
from clubs.models import Member, Club, Application

from django.contrib import messages
from django.urls import reverse
from django.shortcuts import render, redirect

class ApplyToClubView(FormView):
    """Allow the user to apply to some club."""
    form_class = ApplyToClubForm
    template_name = "apply_to_club.html"

    @method_decorator(login_required)
    @method_decorator(club_exists)
    @method_decorator(not_banned)
    def dispatch(self, request, club_id):
        return super().dispatch(request)

    def form_valid(self, form):
        current_user = self.request.user
        desired_club = Club.objects.get(id=self.kwargs['club_id'])

        if Application.objects.filter(club=desired_club, user = current_user).exists():
            messages.add_message(self.request, messages.ERROR, "You have already applied for this club")
        elif Member.objects.filter(club=desired_club, user = current_user).exists():
            messages.add_message(self.request, messages.ERROR, "You are already a member in this club")
        else:    
            self.object = form.save(desired_club, current_user)
            return super().form_valid(form)

        return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['club'] = Club.objects.get(id=self.kwargs['club_id'])
        return context

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, f"Applied to {Club.objects.get(id=self.kwargs['club_id']).name}!")
        return reverse('show_clubs')


@login_required
@club_exists
def withdraw_application_to_club(request, club_id):
    """Have currently logged in user delete an application to the specified club, if it exists."""
    current_user = request.user
    applied_club = Club.objects.get(id=club_id)
    if Application.objects.filter(club=applied_club, user = current_user).exists():
        Application.objects.get(club=applied_club, user=current_user).delete()

    return redirect('show_clubs')