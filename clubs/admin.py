from django.contrib import admin
from .models import User, Club, Application, Member, Ban


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users"""
    list_display = [
        'username', 'first_name', 'last_name', 'email', 'is_active', 'experience', 'bio'
    ]

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for clubs"""
    list_display = [
        'name', 'location', 'description'
    ]

@admin.register(Application)
class applicationAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for applications"""
    list_display = [
        'club', 'user', 'personal_statement'
    ]

@admin.register(Member)
class membershipAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for members"""
    list_display = [
        'club', 'user', 'is_officer', 'is_owner'
    ]

@admin.register(Ban)
class banAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for ban"""
    list_display = [
        'club', 'user'
    ]
