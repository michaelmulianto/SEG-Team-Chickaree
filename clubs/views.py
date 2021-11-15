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
