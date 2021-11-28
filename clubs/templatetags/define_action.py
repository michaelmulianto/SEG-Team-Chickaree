from django import template
from clubs.models import User, Club, Application, Member
register = template.Library()

@register.simple_tag
def count_members(club_to_count):
  return Member.objects.filter(club=club_to_count).count()
