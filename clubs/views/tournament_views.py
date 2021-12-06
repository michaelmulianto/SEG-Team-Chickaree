from django.views import View
from django.views.generic.edit import FormView

from .decorators import login_prohibited
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import OrganiseTournamentForm
from clubs.models import Tournament

from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render

class OrganiseTournamentView(FormView):
    """Create a new tournament."""
    form_class = OrganiseTournamentForm
    template_name = "organise_tournament.html"

    @method_decorator(login_required)
    def dispatch(self, request):
        return super().dispatch(request)

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('show_club')
