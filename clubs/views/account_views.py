"""Views relating to the currently logged in user's account."""

from django.views import View
from django.views.generic.edit import FormView, UpdateView

from .helpers import login_prohibited, get_clubs_of_user
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import SignUpForm, EditAccountForm
from clubs.models import User

from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render

@login_required
def account(request):
    """Render a page displaying the attributes of the currently logged in user."""
    return render(request, 'account.html', {'user': request.user, 'my_clubs':get_clubs_of_user(request.user)})

class SignUpView(FormView):
    """Create a new user account."""
    form_class = SignUpForm
    template_name = "sign_up.html"

    @method_decorator(login_prohibited)
    def dispatch(self, request):
        return super().dispatch(request)

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

class EditAccountView(UpdateView):
    """Edit the details of the currently logged in user."""

    model = User
    template_name = "edit_account.html"
    form_class = EditAccountForm

    @method_decorator(login_required)
    def dispatch(self, request):
        return super().dispatch(request)

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Account Details updated!")
        return reverse('account')

