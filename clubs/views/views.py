"""
Define the views for the system.

"""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from clubs import forms
from django.http import HttpResponseForbidden, request
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.conf import settings
from clubs.forms import LogInForm, SignUpForm, CreateClubForm, EditAccountForm, ApplyToClubForm, EditClubInfoForm
from clubs.models import User, Club, Application, Member, Ban
from .decorators import login_prohibited, club_exists, application_exists, membership_exists, ban_exists, not_banned
from .helpers import is_user_officer_of_club, is_user_owner_of_club, get_clubs_of_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views import View

