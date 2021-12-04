"""Views relating to management of a club."""

from django.views import View
from django.views.generic.edit import FormView, UpdateView

from .helpers import get_clubs_of_user
from .decorators import club_exists
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import CreateClubForm
from clubs.models import Member, Club

from django.urls import reverse
from django.shortcuts import render

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


@login_required
@membership_exists
def transfer_ownership_to_officer(request, member_id):
    """Allow the owner of a club to promote some member of said club to officer."""
    member = Member.objects.get(id = member_id)
    club = member.club
    if not(Member.objects.filter(club=club, user=request.user, is_owner=True).exists()):
        # Access denied, member isn't owner
        return redirect('members_list', club_id=club.id)

    curr_owner = Member.objects.get(club=club, user=request.user)
    if not(member.is_officer):
        # Targetted member should be an officer
        return redirect('members_list', club_id=club.id)

    member.is_owner = True
    member.is_officer = False
    member.save() # Or database won't update.

    curr_owner.is_owner = False
    curr_owner.is_officer = True
    curr_owner.save()
    return redirect('members_list', club_id=club.id)

@login_required
@club_exists
def edit_club_info(request, club_id):
    """Edit the details for the club as an owner."""
    club = Club.objects.get(id = club_id)
    current_user = request.user
    if request.method == 'POST':
        form = forms.EditClubInfoForm(instance = club, data=request.POST)
        if form.is_valid():
                form.save()
                return redirect('show_clubs')
    else:
        form = EditClubInfoForm(instance = club)
    return render(request, 'edit_club_info.html', {'form': form, 'club':Club.objects.get(id = club_id)})