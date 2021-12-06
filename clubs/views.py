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
from clubs.helpers import login_prohibited, club_exists, application_exists, membership_exists, ban_exists, not_banned, is_user_officer_of_club, is_user_owner_of_club, get_clubs_of_user
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
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                redirect_url = next or settings.REDIRECT_URL_WHEN_LOGGED_IN
                return redirect(redirect_url)
            elif User.objects.filter(email=email).exists():
                messages.add_message(request, messages.ERROR, "Wrong password")
        else:
            messages.add_message(request, messages.ERROR, "The credentials provided are invalid!")
    else:
        next = request.GET.get('next') or ''
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form, 'next' : next})
    #return render(request, 'log_in.html', {'title': title+"| Log In", 'form': form}) when title is ready

@login_required
def account(request):
    """Render a page displaying the attributes of the currently logged in user."""
    return render(request, 'account.html', {'user': request.user, 'my_clubs':get_clubs_of_user(request.user)})

@login_required
def my_clubs_list(request):
    current_user = request.user
    my_clubs = []
    for club in Club.objects.all():
        if Application.objects.filter(club=club, user=current_user):
            my_clubs.append(club)
        if Member.objects.filter(club=club, user=current_user):
            my_clubs.append(club)

    paginator = Paginator(my_clubs, settings.CLUBS_PER_PAGE)

    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj  = paginator.page(1)
    except EmptyPage:
        page_obj  = paginator.page(paginator.num_pages)

    return render(request, 'my_clubs_list.html', {'clubs': my_clubs, 'current_user':current_user, 'page_obj':page_obj, 'my_clubs':get_clubs_of_user(request.user)})

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
    return render(request, 'edit_account.html', {'form': form, 'my_clubs':get_clubs_of_user(request.user)})


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
        return render(request, 'create_club.html', {'form': form, 'my_clubs':get_clubs_of_user(request.user)})
    return render(request, 'create_club.html', {'form': CreateClubForm(), 'my_clubs':get_clubs_of_user(request.user)})

@login_required
@club_exists
@not_banned
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
        return render(request, 'apply_to_club.html', {'form': form, 'club':desired_club, 'my_clubs':get_clubs_of_user(request.user)})
    else: # GET
        return render(request, 'apply_to_club.html', {'form': forms.ApplyToClubForm(), 'club':Club.objects.get(id = club_id), 'my_clubs':get_clubs_of_user(request.user)})

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

@login_required
@club_exists
def leave_club(request, club_id):
    """Delete the member object linking the current user to the specified club, iff it exists."""
    current_user = request.user
    applied_club = Club.objects.get(id=club_id)
    if Member.objects.filter(club=applied_club, user = current_user).exists():
        Member.objects.get(club=applied_club, user=current_user).delete()
    return redirect('show_clubs')

@login_required
@membership_exists
def kick_member(request, member_id):
    current_user = request.user
    member = Member.objects.get(id=member_id)
    club = member.club
    if is_user_owner_of_club(current_user, club) or is_user_officer_of_club(current_user, club):
        Member.objects.filter(id=member_id).delete()
    return redirect('members_list', club_id=club.id)

@login_required
@membership_exists
def ban_member(request, member_id):
    current_user = request.user
    member = Member.objects.get(id=member_id)
    club = member.club
    if is_user_owner_of_club(current_user, club) and not is_user_officer_of_club(member.user, club): #Only owners can ban members, not officers.
        Ban.objects.create(club=club, user=member.user)
        Member.objects.filter(id=member_id).delete()
    return redirect('members_list', club_id=club.id)

@login_required
@ban_exists
def unban_member(request, ban_id):
    current_user = request.user
    ban = Ban.objects.get(id=ban_id)
    club = ban.club
    if is_user_owner_of_club(current_user, club):
        Member.objects.create(club=club, user=ban.user)
        Ban.objects.filter(id=ban_id).delete()
    else:
        member = Member.objects.get(club=club, is_owner=True)
        messages.error(request, 'Only the owner can unban users. Please ask ' + member.user.first_name + ' ' + member.user.last_name + ' to perform this action for you.')
    return redirect('members_list', club_id=club.id)


@login_required
def show_clubs(request):
    """Return a list of every club created on the website"""
    clubs = Club.objects.all()
    return render(request, 'show_clubs.html', {'clubs': clubs, 'current_user': request.user, 'my_clubs':get_clubs_of_user(request.user)})

def log_out(request):
    """If a user is logged in, log them out."""
    logout(request)
    return redirect('home')

@login_required
@club_exists
def show_applications_to_club(request, club_id):
    """Allow the owner of a club to view all applications to said club."""
    club_to_view = Club.objects.get(id = club_id)
    if not(Member.objects.filter(club=club_to_view, user=request.user, is_owner=True).exists()):
        # Access denied
        #return redirect('show_clubs', {'my_clubs':get_clubs_of_user(request.user)})
        return redirect('show_clubs')

    applications = Application.objects.filter(club = club_to_view)
    return render(request, 'application_list.html', {'applications': applications, 'my_clubs':get_clubs_of_user(request.user)})

@login_required
@club_exists
def banned_members(request, club_id):
    """Allow the owner of a club to view all applications to said club."""
    club_to_view = Club.objects.get(id = club_id)
    if not is_user_owner_of_club(request.user, club_to_view):
        # Access denied
        messages.error(request, "Only the club owner can view banned members")
        return redirect('show_clubs')

    banned_members = Ban.objects.filter(club = club_to_view)
    return render(request, 'banned_member_list.html', {'club': club_to_view, 'banned_members': banned_members, 'my_clubs':get_clubs_of_user(request.user)})

@login_required
@application_exists
def respond_to_application(request, app_id, is_accepted):
    """Allow the owner of a club to accept or reject some application to said club."""
    application = Application.objects.get(id = app_id)
    club_applied = application.club
    if not(Member.objects.filter(club=application.club, user=request.user, is_owner=True).exists()):
        # Access denied
        return redirect('show_clubs')
    # Create member object iff application is accepted

    if is_accepted:
        Member.objects.create(
            user = application.user,
            club = club_applied
        )

    application.delete() # Remains local python object while in scope.
    applications = Application.objects.all().filter(club = club_applied)
    return redirect("show_applications_to_club", club_id=club_applied.id)

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
    return render(request, 'change_password.html', { 'form': form , 'my_clubs':get_clubs_of_user(request.user)})

@login_required
@club_exists
def show_club(request, club_id):
    """View details of a club."""
    current_user = request.user
    club = Club.objects.get(id=club_id)
    members = Member.objects.filter(club = club_id)
    officers = members.filter(is_officer = True)
    officerCount = officers.count()
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
    return render(request, 'show_club.html', {'current_user': request.user, 'club': club, 'members': numberOfMembers, 'userIsMember': isMember, 'owner': getOwner, 'userIsOwner': isOwner, 'userIsOfficer': isOfficer, 'officers': officers, 'my_clubs':get_clubs_of_user(request.user), 'officerCount': officerCount})

@login_required
@membership_exists
def promote_member_to_officer(request, member_id):
    """Allow the owner of a club to promote some member of said club to officer."""
    member = Member.objects.get(id = member_id)
    club = member.club
    if not(Member.objects.filter(club=club, user=request.user, is_owner=True).exists()):
        # Access denied, member isn't owner
        return redirect('show_clubs')
    member.is_officer = True
    member.save() # Or database won't update.
    return redirect('members_list', club_id=club.id)

@login_required
@membership_exists
def demote_officer_to_member(request, member_id):
    """Allow the owner of a club to promote some member of said club to officer."""
    member = Member.objects.get(id = member_id)
    club = member.club
    if not(Member.objects.filter(club=club, user=request.user, is_owner=True).exists()):
        # Access denied, member isn't owner
        return redirect('show_clubs')
    member.is_officer = False
    member.save() # Or database won't update.
    return redirect('members_list', club_id=club.id)

@login_required
@club_exists
def members_list(request, club_id):
    """Display a list of the members in a club"""
    current_user = request.user
    club = Club.objects.get(id = club_id)
    members = Member.objects.filter(club = club)
    return render(request, 'members_list.html', {'members': members, 'club': club, 'current_user': current_user , 'my_clubs':get_clubs_of_user(request.user)})


@login_required
@membership_exists
def transfer_ownership_to_officer(request, member_id):
    """Allow the owner of a club to promote some member of said club to officer."""
    member = Member.objects.get(id = member_id)
    club = member.club
    if not(Member.objects.filter(club=club, user=request.user, is_owner=True).exists()):
        # Access denied, member isn't owner
        return redirect('members_list', club_id=club.id)

    curr_owner = Member.objects.get(club=club, user=request.user)
    if not(member.is_officer):
        # Targetted member should be an officer
        return redirect('members_list', club_id=club.id)

    curr_owner.is_owner = False
    curr_owner.is_officer = True
    curr_owner.save() # Or database won't update.
    
    member.is_owner = True
    member.is_officer = False
    member.save() # Or database won't update.

    return redirect('members_list', club_id=club.id)

@login_required
@club_exists
def edit_club_info(request, club_id):
    """Edit the details for the club as an owner."""
    club = Club.objects.get(id = club_id)
    current_user = request.user
    if request.method == 'POST':
        form = forms.EditClubInfoForm(instance = club, data=request.POST)
        if form.is_valid():
                form.save()
                return redirect('show_clubs')
    else:
        form = EditClubInfoForm(instance = club)
    return render(request, 'edit_club_info.html', {'form': form, 'club':Club.objects.get(id = club_id), 'my_clubs':get_clubs_of_user(request.user)})
