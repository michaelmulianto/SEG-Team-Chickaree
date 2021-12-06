"""Views related to authenticating a user's identity."""

from django.views import View

from .decorators import login_prohibited
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import LogInForm

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect


class LogInView(View):
    """View to allow an already registered user to log in."""

    http_method_names = ['get', 'post']

    @method_decorator(login_prohibited)
    def dispatch(self, request):
        return super().dispatch(request)

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect(self.next)

        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """If a user is logged in, log them out."""
    logout(request)
    return redirect('home')