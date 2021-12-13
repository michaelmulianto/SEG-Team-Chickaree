"""system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, register_converter
from clubs import views
from . import converters

register_converter(converters.BooleanPathConverter, 'bool')

handler404 = 'clubs.views.errors.page_not_found_custom'
handler500 = 'clubs.views.errors.server_error_custom'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),

    path('account/', views.account, name = 'account'),
    path('account/edit/', views.EditAccountView.as_view(), name = 'edit_account'),
    path('account/change_password/', views.ChangePasswordView.as_view(), name = 'change_password'),

    path('clubs/', views.show_clubs, name = 'show_clubs'),
    path('clubs/my/', views.my_clubs_list, name = 'my_clubs_list'),
    path('clubs/<str:param>/<str:order>/', views.show_clubs, name = 'show_clubs'),

    path('club/create/', views.CreateClubView.as_view(), name='create_club'),
    path('club/<int:club_id>/', views.show_club, name='show_club'),
    path('club/<int:club_id>/edit/', views.EditClubInfoView.as_view(), name='edit_club_info'),
    path('club/<int:club_id>/delete/', views.delete_club, name='delete_club'),
    path('club/<int:club_id>/apply/', views.ApplyToClubView.as_view(), name = 'apply_to_club'),
    path('club/<int:club_id>/withdraw_application/', views.withdraw_application_to_club, name = 'withdraw_application_to_club'),
    path('club/<int:club_id>/leave/', views.leave_club, name = 'leave_club'),
    path('club/<int:club_id>/members/', views.members_list, name='members_list'),
    path('club/<int:club_id>/applications/', views.show_applications_to_club, name='show_applications_to_club'),
    path('club/<int:club_id>/banned_members/', views.banned_members, name='banned_members'),
    path('club/<int:club_id>/organise_tournament/', views.OrganiseTournamentView.as_view(), name='organise_tournament'),

    path('club/<int:tournament_id>/join_tournament/', views.join_tournament, name='join_tournament'),


    path('application/<int:app_id>/respond/<bool:is_accepted>/', views.respond_to_application, name='respond_to_application'),

    path('banned/<int:ban_id>/unban/', views.unban_member, name='unban_member'),

    path('member/<int:member_id>/promote/', views.promote_member_to_officer, name='promote_member_to_officer'),
    path('member/<int:member_id>/demote/', views.demote_officer_to_member, name='demote_officer_to_member'),
    path('member/<int:member_id>/transfer_ownership/', views.transfer_ownership_to_officer, name='transfer_ownership_to_officer'),
    path('member/<int:member_id>/kick/', views.kick_member, name='kick_member'),
    path('member/<int:member_id>/ban/', views.ban_member, name='ban_member'),

    path('tournament/<int:tournament_id>/', views.show_tournament, name='show_tournament'),
    path('tournament/<int:tournament_id>/add_organiser/<int:member_id>', views.add_organisers_to_tournament, name='add_organiser_to_tournament'),
    path('match/<int:match_id>/add_result', views.AddResultView.as_view(), name='add_result')
]
