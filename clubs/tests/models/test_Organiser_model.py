from django.test import TestCase
from clubs.models import KnockoutStage, Club, Match, StageInterface, User, Membership, Participant, Tournament
from django.core.exceptions import ValidationError

class OrganiserModelTestCase(TestCase):

    