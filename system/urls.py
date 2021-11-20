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
from django.urls import path
from clubs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('log_in/', views.log_in, name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('create_club/', views.create_club, name='create_club'),
    path('account/', views.account, name = 'account'),
    path('edit_account/', views.edit_account, name = 'edit_account'),
    path('change_password/', views.change_password, name = 'change_password'),
    path('clubs/', views.show_clubs, name = 'show_clubs'),
    path('apply_to_club/<int:club_id>', views.apply_to_club, name = 'apply_to_club'),
    path('club/<int:club_id>', views.show_club, name='show_club'),
]
