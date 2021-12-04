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

# @login_required
# def create_club(request):
#     """Create a new chess club. Handles club creation form."""
#     if request.method == 'POST':
#         current_user = request.user
#         form = CreateClubForm(request.POST)
#         if form.is_valid():
#             new_club = form.save()
#             Member.objects.create(
#                 club = new_club,
#                 user = current_user,
#                 is_owner = True
#             )
#             return redirect('show_clubs')
#         return render(request, 'create_club.html', {'form': form, 'my_clubs':get_clubs_of_user(request.user)})
#     return render(request, 'create_club.html', {'form': CreateClubForm(), 'my_clubs':get_clubs_of_user(request.user)})