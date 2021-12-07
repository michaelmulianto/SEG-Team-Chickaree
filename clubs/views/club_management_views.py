"""Views relating to management of a club."""

from django.views import View
from django.views.generic.edit import FormView, UpdateView, DeleteView

from .helpers import is_user_owner_of_club
from .decorators import club_exists, membership_exists
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import CreateClubForm, EditClubInfoForm
from clubs.models import Membership, Club

from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect

class CreateClubView(FormView):
    """Create a new club."""
    form_class = CreateClubForm
    template_name = "create_club.html"

    @method_decorator(login_required)
    def dispatch(self, request):
        return super().dispatch(request)

    def form_valid(self, form):
        self.object = form.save()
        Membership.objects.create(
            club = self.object,
            user = self.request.user,
            is_owner = True
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('show_clubs')


@login_required
@membership_exists
def transfer_ownership_to_officer(request, member_id):
    """Allow the owner of a club to promote some member of said club to officer."""
    member = Membership.objects.get(id = member_id)
    club = member.club
    if not(is_user_owner_of_club(request.user, club)):
        # Access denied, member isn't owner
        messages.error(request, 'Only the owner can transfer ownership of a club.')
        return redirect('members_list', club_id=club.id)

    curr_owner = Membership.objects.get(club=club, user=request.user)
    if not(member.is_officer):
        # Targetted member should be an officer
        messages.error(request, 'Ownership must be transfered to an officer. Promote '
            + '@' + member.user.username + ' first.')
        return redirect('members_list', club_id=club.id)

    curr_owner.is_owner = False
    curr_owner.is_officer = True
    curr_owner.save()

    member.is_owner = True
    member.is_officer = False
    member.save() # Or database won't update.

    messages.warning(request, 'Ownership transfered to ' + '@' + member.user.username + '.')
    return redirect('members_list', club_id=club.id)

class EditClubInfoView(UpdateView):
    """Edit the details of a given club."""

    model = Club
    template_name = "edit_club_info.html"
    form_class = EditClubInfoForm

    @method_decorator(login_required)
    @method_decorator(club_exists)
    def dispatch(self, request, club_id):
        return super().dispatch(request)

    def get_object(self):
        """Return the object (club) to be updated."""
        return Club.objects.get(id=self.kwargs['club_id'])

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Club Details updated!")
        return reverse('show_clubs')

@login_required
@club_exists
def delete_club(request, club_id):
    """Delete the club, you must be the owner in order to delete the club"""
    current_user = request.user
    club_to_delete = Club.objects.get(id=club_id)

    if is_user_owner_of_club(current_user, club_to_delete):
        Club.objects.get(id=club_id).delete()
        messages.add_message(request, messages.INFO, "The club has successfully been deleted")
        return redirect('show_clubs')
    else:
        messages.add_message(request, messages.WARNING, "You are not the owner of this clubs")
        return redirect('show_clubs')
