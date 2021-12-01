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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('log_in/', views.log_in, name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('create_club/', views.create_club, name='create_club'),
    path('account/', views.account, name = 'account'),
    path('account/my_clubs/', views.my_clubs_list, name = 'my_clubs_list'),
    path('edit_account/', views.edit_account, name = 'edit_account'),
    path('change_password/', views.change_password, name = 'change_password'),
    path('show_clubs/', views.show_clubs, name = 'show_clubs'),
    path('apply_to_club/<int:club_id>', views.apply_to_club, name = 'apply_to_club'),
    path('withdraw_application_to_club/<int:club_id>', views.withdraw_application_to_club, name = 'withdraw_application_to_club'),
    path('leave_club/<int:club_id>', views.leave_club, name = 'leave_club'),
    path('application/<int:app_id>/respond/<bool:is_accepted>', views.respond_to_application, name='respond_to_application'),
    path('members_list/<int:club_id>', views.members_list, name='members_list'),
    path('club/<int:club_id>', views.show_club, name='show_club'),
    path('club/<int:club_id>/applications', views.show_applications_to_club, name='show_applications_to_club'),
    path('kick_member/<int:member_id>', views.kick_member, name='kick_member'),
    path('promote_member/<int:member_id>', views.promote_member_to_officer, name='promote_member_to_officer'),
    path('demote_officer/<int:member_id>', views.demote_officer_to_member, name='demote_officer_to_member'),
]
