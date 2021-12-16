"""Views relating to club applications."""

from django.views import View
from django.views.generic.edit import FormView

from .helpers import is_user_owner_of_club, is_user_officer_of_club
from .decorators import club_exists, membership_exists, not_banned, application_exists
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import ApplyToClubForm
from clubs.models import Membership, Club, Application

from django.contrib import messages
from django.urls import reverse
from django.shortcuts import render, redirect

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.conf import settings

# User applying to club views:

class ApplyToClubView(FormView):
    """Allow the user to apply to some club."""
    form_class = ApplyToClubForm
    template_name = "club/apply_to_club.html"

    @method_decorator(login_required)
    @method_decorator(club_exists)
    @method_decorator(not_banned)
    def dispatch(self, request, club_id):
        return super().dispatch(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.request.user
        context['club'] = Club.objects.get(id=self.kwargs['club_id'])
        return context

    def form_valid(self, form):
        current_user = self.request.user
        desired_club = self.get_context_data()['club']

        if Application.objects.filter(club=desired_club, user = current_user).exists():
            messages.add_message(self.request, messages.ERROR, "You have already applied for this club")
        elif Membership.objects.filter(club=desired_club, user = current_user).exists():
            messages.add_message(self.request, messages.ERROR, "You are already a member in this club")
        else:
            self.object = form.save(desired_club, current_user)
            return super().form_valid(form)

        return self.form_invalid(form)

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, f"Applied to {self.get_context_data()['club'].name}!")
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

# Owner viewing application views:

@login_required
@club_exists
def show_applications_to_club(request, club_id):
    """Allow the owner of a club to view all applications to said club."""
    club_to_view = Club.objects.get(id = club_id)
    if is_user_owner_of_club(request.user, club_to_view) or is_user_officer_of_club(request.user, club_to_view):

        paginator = Paginator(club_to_view.get_applications(), settings.APPLICATIONS_PER_PAGE)

        page = request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj  = paginator.page(1)
        except EmptyPage:
            page_obj  = paginator.page(paginator.num_pages)

        return render(request, 'club/application_list.html', {'current_user': request.user, 'club': club_to_view, 'applications': page_obj})
    else: #Access denied
        messages.error(request, "Only the club owner and officers can view applications")
        return redirect('show_club', club_id=club_id)

@login_required
@application_exists
def respond_to_application(request, app_id, is_accepted):
    """Allow the owner of a club to accept or reject some application to said club."""
    application = Application.objects.get(id = app_id)
    club_applied_to = application.club
    if is_user_owner_of_club(request.user, club_applied_to) or is_user_officer_of_club(request.user, club_applied_to):
        if is_accepted: #Applications are delete wether rejected or accepted but iff accepted a membership is created.
            Membership.objects.create(
                user = application.user,
                club = club_applied_to
            )
            messages.success(request, '@' + application.user.username + ' was accepted.')
        else:
            messages.warning(request, '@' + application.user.username + ' was rejected.')
        application.delete() # Remains local python object while in scope.
        return redirect("show_applications_to_club", club_id=club_applied_to.id)
    else:
        messages.error(request, 'Only owners or officers can accept or reject applications.')
        return redirect("show_club", club_id=club_applied_to.id)
