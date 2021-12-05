"""Views relating to club applications."""

from django.views import View
from django.views.generic.edit import FormView, UpdateView

from .helpers import get_clubs_of_user
from .decorators import club_exists, membership_exists, not_banned
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.forms import ApplyToClubForm
from clubs.models import Member, Club, Application

from django.contrib import messages
from django.urls import reverse
from django.shortcuts import render, redirect

@login_required
@club_exists
@not_banned
def apply_to_club(request, club_id):
    """Have currently logged in user create an application to a specified club."""
    if request.method == 'POST':
        desired_club = Club.objects.get(id = club_id)
        current_user = request.user
        form = ApplyToClubForm(request.POST)
        if form.is_valid():
            if not(Application.objects.filter(club=desired_club, user = current_user).exists()) and not(Member.objects.filter(club=desired_club, user = current_user).exists()):
                form.save(desired_club, current_user)
                return redirect('show_clubs')
        # Else: Invalid form/Already applied/Already member
        if Application.objects.filter(club=desired_club, user = current_user).exists():
            messages.add_message(request, messages.ERROR, "You have already applied for this club")
        elif Member.objects.filter(club=desired_club, user = current_user).exists():
            messages.add_message(request, messages.ERROR, "You are already a member in this club")
        return render(request, 'apply_to_club.html', {'form': form, 'club':desired_club, 'my_clubs':get_clubs_of_user(request.user)})
    else: # GET
        return render(request, 'apply_to_club.html', {'form': ApplyToClubForm(), 'club':Club.objects.get(id = club_id), 'my_clubs':get_clubs_of_user(request.user)})

@login_required
@club_exists
def withdraw_application_to_club(request, club_id):
    """Have currently logged in user delete an application to the specified club, if it exists."""
    current_user = request.user
    applied_club = Club.objects.get(id=club_id)
    if Application.objects.filter(club=applied_club, user = current_user).exists():
        Application.objects.get(club=applied_club, user=current_user).delete()
        return redirect('show_clubs')
    return redirect('show_clubs')