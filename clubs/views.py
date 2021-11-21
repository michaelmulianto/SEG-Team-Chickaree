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
from django.http import Http404
from django.shortcuts import render, redirect
from .forms import LogInForm, SignUpForm, ApplyToClubForm
from django.contrib import messages
from clubs import forms
from django.http import HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from clubs.models import User, Club, Application, Member

def home(request):
    # Default view for visitors.
    if request.user.is_authenticated:
        return redirect('account')

    return render(request, 'home.html')

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


def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('account')
        messages.add_message(request, messages.ERROR, "The credentials provided are invalid!")
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form})
    #return render(request, 'log_in.html', {'title': title+"| Log In", 'form': form}) when title is ready

def account(request):
    if request.user.is_authenticated:
        try:
            #find the appropriate user
            user = request.user
        except ObjectDoesNotExist:
             return redirect('no_account_found')

             #if found show their information
        else:
            return render(request, 'account.html', {'user': request.user})
    else:
        return redirect("home")


def create_club(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            current_user = request.user
            form = forms.CreateClubForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('show_clubs')
            else:
                return render(request, 'create_club.html', {'form': form})
        else:
            return redirect('log_in')
    else:
        return render(request, 'create_club.html', {'form': forms.CreateClubForm()})

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
