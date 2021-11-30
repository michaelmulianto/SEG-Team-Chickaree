from django import template
from clubs.models import User, Club, Application, Member
register = template.Library()

@register.simple_tag
def count_members(club_to_count):
  return Member.objects.filter(club=club_to_count).count()

@register.simple_tag
def check_has_applied(club_to_check, current_user):
  return Application.objects.filter(club=club_to_check, user=current_user).exists()

@register.simple_tag
def check_is_member(club_to_check, current_user):
  return Member.objects.filter(club=club_to_check, user=current_user).exists()

@register.simple_tag
def check_is_officer(club_to_check, current_user):
  return Member.objects.filter(club=club_to_check, user=current_user, is_officer=True).exists()

@register.simple_tag
def check_is_owner(club_to_check, current_user):
  return Member.objects.filter(club=club_to_check, user=current_user, is_owner=True).exists()
