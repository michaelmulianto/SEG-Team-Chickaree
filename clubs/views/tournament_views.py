from django.http import request
from django.views import View

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from clubs.models import Tournament, Club, Organiser, Membership, Participant, GroupStage, KnockoutStage, MemberTournamentRelationship

from .decorators import club_exists, tournament_exists, membership_exists
from .helpers import is_user_organiser_of_tournament, is_user_owner_of_club, is_user_officer_of_club, is_lead_organiser_of_tournament, is_participant_in_tournament


from datetime import datetime
from django.utils.timezone import now

from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404

@login_required
@tournament_exists
def show_tournament(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    club = tournament.club
    if Membership.objects.filter(user=request.user, club=club).exists():
        tournament_group_stages = list(reversed(GroupStage.objects.filter(tournament=tournament)))
        tournament_knockout_stages = list(reversed(KnockoutStage.objects.filter(tournament=tournament)))
        return render(request, 'tournament/show_tournament.html', {
                'current_user': request.user,
                'tournament': tournament,
                'tournament_group_stages': tournament_group_stages,
                'tournament_knockout_stages': tournament_knockout_stages,
            }
        )
    else:
        messages.error(request, "You are not a member of the club that organises this tournament, you can view the basic tournament details from the club's page.")
    return redirect('show_club', club_id=club.id)

@login_required
@tournament_exists
def show_tournament_participants(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    club = tournament.club
    if Membership.objects.filter(user=request.user, club=club).exists():
        return render(request, 'tournament/show_tournament_participants.html', {
                'current_user': request.user,
                'tournament': tournament
            }
        )
    else:
        messages.error(request, "You are not a member of the club that organises this tournament, you can view the basic tournament details from the club's page.")
    return redirect('show_club', club_id=club.id)

@login_required
@tournament_exists
def withdraw_participation_from_tournament(request, tournament_id):
    """Have currently logged in user withdraw from a tournament, if it exists."""
    tournament = Tournament.objects.get(id=tournament_id)
    member = get_object_or_404(Membership, user = request.user, club = tournament.club)

    if Participant.objects.filter(tournament=tournament, member=member).exists():
        if tournament.deadline > now():
            Participant.objects.get(tournament=tournament, member=member).delete()
        else:
            messages.error(request, 'You cannot withdraw from the tournament as the deadline has passed.')
    else:
        messages.error(request, 'You have not participated in this tournament, ' + str(tournament.name) + '.')

    return redirect('show_club', club_id=tournament.club.id)

@login_required
@tournament_exists
def join_tournament(request, tournament_id):
    tour = Tournament.objects.get(id = tournament_id)
    member = get_object_or_404(Membership, user = request.user, club = tour.club)
    is_not_organiser = Organiser.objects.filter(member = member, tournament = tour).count() == 0
    is_in_tournament = Participant.objects.filter(member = member, tournament = tour).count() > 0

    current_capacity = Participant.objects.filter(tournament = tour)
    if(current_capacity.count() < tour.capacity):
        if(is_not_organiser == True):
            if(member != None):
                if(is_in_tournament == False):
                    participant = Participant.objects.create(
                        member = member,
                        tournament = tour
                    )
                else:
                    messages.error(request, 'You are already enrolled in the tournament')
            else:
                messages.error(request, 'You are not a member of the club and cannot join the tournament')
        else:
            messages.error(request, 'You are the organizer of the tournament and are not allowed to join it')
    else:
        messages.error(request, 'Tournament is full')

    return redirect('show_club', club_id=tour.club.id)

@login_required
def my_tournaments_list(request):
    current_user = request.user
    my_tournaments = [
        [[],[],[]], # Participant... past/present/future
        [[],[],[]] # Organiser
    ]
    
    curr_time = now()
    
    for tournament in Tournament.objects.all():
        if Membership.objects.filter(user=current_user, club=tournament.club).exists():
            if Participant.objects.filter(tournament=tournament, user=current_user).exists():
                outer_index=0
            elif Organiser.objects.filter(tournament=tournament, user=current_user).exists():
                outer_index=1
            else:
                outer_index=None
            
            if outer_index:
                if tournament.end <= curr_time:
                    inner_index = 0
                elif tournament.start <= curr_time:
                    inner_index = 1
                else:
                    inner_index = 2
                    
                my_tournaments[outer_index][inner_index].append(tournament)
    
    return render(request, 'tournament/my_tournament_list.html', {
                'current_user': request.user,
                'participant_tournaments_past': my_tournaments[0][0],
                'participant_tournaments_present': my_tournaments[0][1],
                'participant_tournaments_future': my_tournaments[0][2],
                'organiser_tournaments_past': my_tournaments[1][0],
                'organiser_tournaments_present': my_tournaments[1][1],
                'organiser_tournaments_future': my_tournaments[1][2],
            }
        )
            