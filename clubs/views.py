"""
Define the views for the system.

Currently implemented views:
    - home
    - sign_up
    - log_in
    - account
    - create clubs
    - show_clubs
    - show_club
"""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from clubs import forms
from django.http import HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings
from clubs.forms import LogInForm, SignUpForm, CreateClubForm, EditAccountForm, ApplyToClubForm
from clubs.models import User, Club, Application, Member
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from clubs.helpers import login_prohibited

@login_prohibited
def home(request):
    # Default view for visitors.
    if request.user.is_authenticated:
        return redirect('account')

    return render(request, 'home.html')

@login_prohibited
def sign_up(request):
    # View to allow user to create account.
    # If POST, form has been submitted.
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('account')

    # If not POST, visitor is trying to view the form e.g. via home
    else:
        form = SignUpForm()

    return render(request, 'sign_up.html', {'form': form})

@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        next = request.POST.get('next') or ''
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                redirect_url = next or settings.REDIRECT_URL_WHEN_LOGGED_IN
                return redirect(redirect_url)
        messages.add_message(request, messages.ERROR, "The credentials provided are invalid!")
    else:
        next = request.GET.get('next') or ''
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form, 'next' : next})
    #return render(request, 'log_in.html', {'title': title+"| Log In", 'form': form}) when title is ready

@login_required
def account(request):
    try:
        #find the appropriate user
        user = request.user
    except ObjectDoesNotExist:
         return redirect('no_account_found')

         #if found show their information
    else:
        return render(request, 'account.html', {'user': user})



@login_required
def edit_account(request):
    current_user = request.user
    if request.method == 'POST':
        form = EditAccountForm(instance = current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Account Details updated!")
            form.save()
            return redirect('account')
    else:
        #make form with the current user information
        form = EditAccountForm(instance = current_user)
    return render(request, 'edit_account.html', {'form': form})



@login_required
def create_club(request):
    if request.method == 'POST':
        current_user = request.user
        form = CreateClubForm(request.POST)
        if form.is_valid():
            new_club = form.save()
            Member.objects.create(
                club = new_club,
                user = current_user,
                isOwner = True
            )
            return redirect('show_clubs')
        else:
            return render(request, 'create_club.html', {'form': form})
    else:
        return render(request, 'create_club.html', {'form': CreateClubForm()})

@login_required
def apply_to_club(request, club_id):
    desired_club = Club.objects.get(id = club_id)
    current_user = request.user
    # Ensure that the user does not have an existing application or membership to the club.
    if not(Application.objects.filter(club=desired_club, user = current_user).exists()) and not(Member.objects.filter(club=desired_club, user = current_user).exists()):
        Application.objects.create(
            user = current_user,
            club = desired_club,
        )
    return redirect('show_clubs')

def apply_to_club(request, club_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            desired_club = Club.objects.get(id = club_id)
            current_user = request.user
            form = forms.ApplyToClubForm(request.POST)
            if form.is_valid():
                if not(Application.objects.filter(club=desired_club, user = current_user).exists()) and not(Member.objects.filter(club=desired_club, user = current_user).exists()):
                    application = Application.objects.create(
                        club = desired_club,
                        user = current_user,
                        experience = form.cleaned_data.get('experience'),
                        personalStatement = form.cleaned_data.get('personalStatement'),
                    )
                    return redirect('show_clubs')
            # Next line executes if one of the last 2 conditionals fail.
            return render(request, 'apply_to_club.html', {'form': form, 'club':desired_club})
        else:
            return redirect('log_in')
    else:
        return render(request, 'apply_to_club.html', {'form': forms.ApplyToClubForm(), 'club':Club.objects.get(id = club_id)})

def show_clubs(request):
    clubs = Club.objects.all()
    return render(request, 'show_clubs.html', {'my_clubs': clubs})

def show_club(request, club_id):
    try:
        club = Club.objects.get(id = club_id)
    except ObjectDoesNotExist:
        return redirect('show_clubs')
    else:
        return render(request, 'show_club.html', {'club': club})

def log_out(request):
    logout(request)
    return redirect('home')

@login_required
def show_applications_to_club(request, club_id):
    current_user = request.user
    try:
        club_to_view = Club.objects.get(id = club_id)
    except ObjectDoesNotExist:
        #Club matching id does not exist. 
        return redirect('show_clubs')
    
    if not(Member.objects.filter(club=club_to_view, user=current_user, isOwner=True).exists()):
        # Access denied
        return redirect('show_clubs')

    applications = Application.objects.all().filter(club = club_to_view)
    return render(request, 'application_list.html', {'applications': applications})

@login_required
def respond_to_application(request, app_id, is_accepted):
    current_user = request.user
    try:
        application = Application.objects.get(id = app_id)
    except ObjectDoesNotExist:
        #Application matching id does not exist. 
        return redirect('show_clubs')
        
    if not(Member.objects.filter(club=application.club, user=current_user, isOwner=True).exists()):
        # Access denied
        return redirect('show_clubs')

    # Create member object iff application is accepted
    if is_accepted:
        Member.objects.create(
            user = application.user,
            club = application.club
        )

    application.delete() # Remains local python object while in scope.
    applications = Application.objects.all().filter(club = application.club)
    return render(request, 'application_list.html', {'applications': applications})
  
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('account')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })

@login_required
def club_details(request, club_id):
    #find the appropriate club
    current_user = request.user
    club = Club.objects.get(id = club_id)
    members = Member.objects.filter(club = club_id)
    numberOfMembers = members.count()
    checkUserisMember = members.filter(user = current_user)
    isMember = False
    if checkUserisMember.count() > 0:
        isMember = True

    return render(request, 'club_details.html', {'club': club, 'members': numberOfMembers, 'userIsMember': isMember})

@login_required
def promote_member_to_officer(request, club_id, member_id):
    current_user = request.user
    try:
        member = Member.objects.get(id = member_id)
    except ObjectDoesNotExist:
        #Member matching id does not exist. 
        #MAKE THIS MEMBERLIST
        return redirect('show_clubs')
        
    if not(Member.objects.filter(club=member.club, user=current_user, isOwner=True).exists()):
        # Access denied
        # If club doesnt exist, show_club should handle the exception.
        return redirect('show_club', kwargs={'club_id':club_id})
        
    member.isOfficer = True 
    member.save() # Or database won't update.
    
    #MAKE THIS MEMBERLIST
    return redirect('show_clubs')