"""Views relating to management of a club."""

from django.views import View
from django.views.generic.edit import FormView, UpdateView

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import CreateClubForm
from clubs.models import Member

from django.urls import reverse

class CreateClubView(FormView):
    """Create a new club."""
    form_class = CreateClubForm
    template_name = "create_club.html"

    @method_decorator(login_required)
    def dispatch(self, request):
        return super().dispatch(request)

    def form_valid(self, form):
        self.object = form.save()
        Member.objects.create(
            club = self.object,
            user = self.request.user,
            is_owner = True
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('show_clubs')