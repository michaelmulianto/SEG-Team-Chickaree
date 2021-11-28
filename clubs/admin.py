from django.contrib import admin
from .models import User, Club, Application, Member


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users"""
    list_display = [
        'username', 'first_name', 'last_name', 'email', 'is_active'
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
        'club', 'user', 'experience', 'personal_statement'
    ]

@admin.register(Member)
class applicationAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for members"""
    list_display = [
        'club', 'user', 'isOfficer', 'isOwner'
    ]
