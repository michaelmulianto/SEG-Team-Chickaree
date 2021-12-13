"""Views related to the running of a tournament"""
from django.views.generic.edit import UpdateView

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect

from clubs.forms import AddResultForm
from clubs.models import Match

class AddResultView(UpdateView):
    """Edit the details of the currently logged in user."""

    model = Match
    template_name = "temporary_add_result.html"
    form_class = AddResultForm

    @method_decorator(login_required)
    def dispatch(self, request, match_id):
        return super().dispatch(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.request.user
        context['match'] = Match.objects.get(id=kwargs['match_id'])
        return context

    def get_object(self):
        """Return the object (match) to be updated."""
        return self.get_context_data()['match']

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Result Registered!")
        return reverse('show_clubs')