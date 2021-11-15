"""
Define the views for the system.

Currently implemented views:
    - home
    - sign_up
"""

from django.shortcuts import render, redirect
from clubs import forms

def home(request):
    # Default view for visitors.
    # This should redirect logged in users somewhere eventually.
    return render(request, 'home.html')

def sign_up(request):
    # View to allow user to create account.
    # If POST, form has been submitted.
    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Temporary redirect to indicate success.
            # (failure renders same page again)
            # Should redirect somewhere more appropriate eventually,
            # for example some sort of user page. Should also log user in.
            return redirect('home')

    # If not POST, visitor is trying to view the form e.g. via home
    else:
        form = forms.SignUpForm()

    return render(request, 'sign_up.html', {'form': form})

def create_club(request):
    #View to allow user to create club
    #If POST, form has been submitted
    if request.method == 'POST':
        form = CreateClubForm(request.POST)
        if request.user.is_authenticated:
            if form.is_valid():
                Post.objects.create(
                    owner = request.user,
                    name = form.cleaned_data['name'],
                    location = form.cleaned_data['location'],
                    description = form.cleaned_data['description']
                )
                #Temporary redirect
                return redirect('home')
        else:
            messages.error(request, "Log in required to create a club")
    else:
        form = CreateClubForm()
    return render(request, 'home.html', {'form': form})
