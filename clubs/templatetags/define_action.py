from django import template
from clubs.models import User, Club, Application, Membership
register = template.Library()

@register.simple_tag
def count_members(club_to_count):
  return Membership.objects.filter(club=club_to_count).count()

@register.simple_tag
def get_owner(club_to_count):
  return Membership.objects.get(club=club_to_count, is_owner=True)

@register.simple_tag
def get_officers(club_to_count):
  return Membership.objects.filter(club=club_to_count, is_officer=True)

@register.simple_tag
def check_has_applied(club_to_check, user):
  return Application.objects.filter(club=club_to_check, user=user).exists()

@register.simple_tag
def check_is_member(club_to_check, user):
  return Membership.objects.filter(club=club_to_check, user=user).exists()

@register.simple_tag
def check_is_officer(club_to_check, user):
  return Membership.objects.filter(club=club_to_check, user=user, is_officer=True).exists()

@register.simple_tag
def check_is_owner(club_to_check, user):
  return Membership.objects.filter(club=club_to_check, user=user, is_owner=True).exists()
