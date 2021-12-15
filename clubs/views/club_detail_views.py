"""Views relating to viewing a club and general member facing views."""

from django.views import View
from django.contrib import messages

from django.utils import timezone
from .helpers import is_user_owner_of_club
from .decorators import club_exists, membership_exists, club_exists
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from django.utils.decorators import method_decorator

from clubs.models import Membership, Club, Tournament

from django.shortcuts import render, redirect

@login_required
@club_exists
def members_list(request, club_id):
    """Display a list of the members in a club"""
    club = Club.objects.get(id = club_id)
    return render(request, 'club/members_list.html', {'current_user': request.user, 'club': club})

@login_required
@club_exists
def show_club(request, club_id):
    """View details of a club."""
    club = Club.objects.get(id=club_id)

    today = timezone.now()
    ongoing_t = Tournament.objects.filter(club=club, start__lte=today, end__gte=today)
    upcoming_t = Tournament.objects.filter(club=club, start__gte=today)
    past_t = Tournament.objects.filter(club=club, end__lte=today)

    return render(
        request,
        'club/show_club.html', {
            'current_user': request.user,
            'club': club,
            'ongoing_tournaments': ongoing_t,
            'upcoming_tournaments': upcoming_t,
            'past_tournaments': past_t
        }
    )

@login_required
@club_exists
def leave_club(request, club_id):
    """Delete the member object linking the current user to the specified club, if it exists."""
    current_user = request.user
    club_to_leave = Club.objects.get(id=club_id)

    if Membership.objects.filter(club=club_to_leave, user=current_user).exists():
        if not is_user_owner_of_club(current_user, club_to_leave):
            Membership.objects.get(club=club_to_leave, user=current_user).delete()
            messages.warning(request, 'You left the ' + club_to_leave.name + ' club.')
            return redirect('show_clubs')
        else:
            messages.error(request, 'You are the owner. You cannot you cannot leave your club. Transfer ownership before leaving or delete the club.')
    else:
        messages.error(request, 'You do not belong to the ' + club_to_leave.name + ' club.')

    return redirect('show_club', club_id=club_to_leave.id)
