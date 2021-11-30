"""
Define the views for the system.

"""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from clubs import forms
from django.http import HttpResponseForbidden, request
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.conf import settings
from clubs.forms import LogInForm, SignUpForm, CreateClubForm, EditAccountForm, ApplyToClubForm
from clubs.models import User, Club, Application, Member
from clubs.helpers import login_prohibited
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

@login_prohibited
def home(request):
    """Generic splash page view for non-logged in user."""
    return render(request, 'home.html')

@login_prohibited
def sign_up(request):
    """View to allow user to create an account, and thus a corresponding user object."""
    # If POST, form has been submitted.
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    # If not POST, visitor is trying to view the form e.g. via home
    else:
        form = SignUpForm()

    return render(request, 'sign_up.html', {'form': form})

@login_prohibited
def log_in(request):
    """View to allow an already registered user to log in."""
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
    """Render a page displaying the attributes of the currently logged in user."""
    user = request.user
    return render(request, 'account.html', {'user': user})

@login_required
def my_clubs_list(request):
    current_user = request.user
    my_clubs = []
    for club in Club.objects.all():
        if Application.objects.filter(club=club, user=current_user).exists():
            my_clubs.append(club)
        if Member.objects.filter(club=club, user=current_user).exists():
            my_clubs.append(club)

    paginator = Paginator(my_clubs, settings.CLUBS_PER_PAGE)

    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj  = paginator.page(1)
    except EmptyPage:
        page_obj  = paginator.page(paginator.num_pages)

    return render(request, 'my_clubs_list.html', {'clubs': my_clubs, 'current_user':current_user, 'page_obj':page_obj})

# class MyClubsListView(LoginRequiredMixin, ListView):
#     model = Club
#     template_name = "my_clubs_list.html"
#     context_object_name = "my_clubs"
#     paginate_by = settings.CLUBS_PER_PAGE

#     current_user = request.user

#     def get_context_data(self, *args, **kwargs):
#         """Generate content to be displayed on the template"""

#         context = super().get_context_data(*args, **kwargs)
#         context["clubs"] = Application.objects.filter(user=current_user) + Member.objects.filter(user=user)
#         context['current_user'] = current_user


@login_required
def edit_account(request):
    """Edit the details for the currently logged in user."""
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
    """Create a new chess club. Handles club creation form."""
    if request.method == 'POST':
        current_user = request.user
        form = CreateClubForm(request.POST)
        if form.is_valid():
            new_club = form.save()
            Member.objects.create(
                club = new_club,
                user = current_user,
                is_owner = True
            )
            return redirect('show_clubs')
        else:
            return render(request, 'create_club.html', {'form': form})
    else:
        return render(request, 'create_club.html', {'form': CreateClubForm()})

@login_required
def apply_to_club(request, club_id):
    """Have currently logged in user create an application to a specified club."""
    if request.method == 'POST':
        desired_club = Club.objects.get(id = club_id)
        current_user = request.user
        form = forms.ApplyToClubForm(request.POST)
        if form.is_valid():
            if not(Application.objects.filter(club=desired_club, user = current_user).exists()) and not(Member.objects.filter(club=desired_club, user = current_user).exists()):
                form.save(desired_club, current_user)
                return redirect('show_clubs')
        # Else: Invalid form/Already applied/Already member
        if Application.objects.filter(club=desired_club, user = current_user).exists():
            messages.add_message(request, messages.ERROR, "You have already applied for this club")
        elif Member.objects.filter(club=desired_club, user = current_user).exists():
            messages.add_message(request, messages.ERROR, "You are already a member in this club")
        return render(request, 'apply_to_club.html', {'form': form, 'club':desired_club})
    else: # GET
        return render(request, 'apply_to_club.html', {'form': forms.ApplyToClubForm(), 'club':Club.objects.get(id = club_id)})

@login_required
def withdraw_application_to_club(request, club_id):
    """Have currently logged in user delete an application to the specified club, if it exists."""
    current_user = request.user
    applied_club = Club.objects.get(id=club_id)
    if Application.objects.filter(club=applied_club, user = current_user).exists() and not(Member.objects.filter(club=applied_club, user = current_user).exists()):
        Application.objects.get(club=applied_club, user=current_user).delete()
        return redirect('show_clubs')
    return redirect('show_clubs')

@login_required
def leave_club(request, club_id):
    """Delete the member object linking the current user to the specified club, iff it exists."""
    current_user = request.user
    applied_club = Club.objects.get(id=club_id)
    if Member.objects.filter(club=applied_club, user = current_user).exists():
        Member.objects.get(club=applied_club, user=current_user).delete()
        return redirect('show_clubs')
    return redirect('show_clubs')

@login_required
def show_clubs(request):
    """Return a list of every club created on the website"""
    clubs = Club.objects.all()
    return render(request, 'show_clubs.html', {'clubs': clubs, 'current_user': request.user})

def log_out(request):
    """If a user is logged in, log them out."""
    logout(request)
    return redirect('home')

@login_required
def show_applications_to_club(request, club_id):
    """Allow the owner of a club to view all applications to said club."""
    current_user = request.user
    try:
        club_to_view = Club.objects.get(id = club_id)
    except ObjectDoesNotExist:
        #Club matching id does not exist.
        return redirect('show_clubs')

    if not(Member.objects.filter(club=club_to_view, user=current_user, is_owner=True).exists()):
        # Access denied
        return redirect('show_clubs')

    applications = Application.objects.all().filter(club = club_to_view)
    return render(request, 'application_list.html', {'applications': applications})

@login_required
def respond_to_application(request, app_id, is_accepted):
    """Allow the owner of a club to accept or reject some application to said club."""
    current_user = request.user
    try:
        application = Application.objects.get(id = app_id)
    except ObjectDoesNotExist:
        #Application matching id does not exist
        return redirect('show_clubs')

    if not(Member.objects.filter(club=application.club, user=current_user, is_owner=True).exists()):
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
    """Allow currently logged in user to change their password."""
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
    return render(request, 'change_password.html', { 'form': form })

@login_required
def show_club(request, club_id):
    """View details of a club."""
    current_user = request.user
    try:
        club = Club.objects.get(id = club_id)
    except ObjectDoesNotExist:
        return redirect('show_clubs')
    members = Member.objects.filter(club = club_id)
    getOwner = members.get(is_owner = True)
    numberOfMembers = members.count()
    checkUserisMember = members.filter(user = current_user)
    isMember = False
    isOwner = False
    isOfficer = False
    if checkUserisMember.filter(is_owner = True).count() > 0:
        isOwner = True
    if checkUserisMember.count() > 0:
        isMember = True
    if checkUserisMember.filter(is_officer = True).count() > 0:
        isOfficer = True
    return render(request, 'show_club.html', {'club': club, 'members': numberOfMembers, 'userIsMember': isMember, 'owner': getOwner, 'userIsOwner': isOwner, 'userIsOfficer': isOfficer})

@login_required
def promote_member_to_officer(request, club_id, member_id):
    """Allow the owner of a club to promote some member of said club to officer."""
    current_user = request.user
    try:
        member = Member.objects.get(id = member_id)
    except ObjectDoesNotExist:
        #Member matching id does not exist.
        return redirect('members_list', club_id=club_id)

    if member.club.id != club_id:
        # Member and club ids do not correspond
        return redirect('members_list', club_id=club_id)
        # I realise this is the same above, but we might want to change where this goes eventually.

    if not(Member.objects.filter(club=member.club, user=current_user, is_owner=True).exists()):
        # Access denied
        # If club doesnt exist, show_club should handle the exception.
        return redirect('show_club', club_id=club_id)

    member.is_officer = True
    member.save() # Or database won't update.

    return redirect('members_list', club_id=club_id)

@login_required
def members_list(request, club_id):
    current_user = request.user
    try:
        club = Club.objects.get(id = club_id)
        members = Member.objects.filter(club = club)
        is_officer = Member.objects.filter(club=club, user=current_user, is_officer=True).exists()
        is_owner = Member.objects.filter(club=club, user=current_user, is_owner=True).exists()
    except ObjectDoesNotExist:
        return redirect('show_club', club_id=club_id)
    else:
        return render(request, 'members_list.html', {'members': members, 'club': club, 'curr_user_is_officer': is_officer, 'curr_user_is_owner': is_owner})
