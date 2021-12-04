"""Views relating to management of a club."""

from django.views import View
from django.views.generic.edit import FormView, UpdateView

from .helpers import get_clubs_of_user
from .decorators import club_exists
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import CreateClubForm
from clubs.models import Member, Club

from django.urls import reverse, render

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

@login_required
@club_exists
def show_club(request, club_id):
    """View details of a club."""
    current_user = request.user
    club = Club.objects.get(id=club_id)
    members = Member.objects.filter(club = club_id)
    officers = members.filter(is_officer = True)
    get_owner = members.get(is_owner = True)
    num_members = members.count()
    check_user_is_member = members.filter(user = current_user)
    is_member = False
    is_owner = False
    is_officer = False
    if check_user_is_member.filter(is_owner = True).count() > 0:
        is_owner = True
    if check_user_is_member.count() > 0:
        is_member = True
    if check_user_is_member.filter(is_officer = True).count() > 0:
        is_officer = True
    return render(request, 'show_club.html', {'club': club, 'members': num_members, 'userIsMember': is_member, 'owner': get_owner, 'userIsOwner': is_owner, 'userIsOfficer': is_officer, 'officers': officers, 'my_clubs':get_clubs_of_user(request.user)})
