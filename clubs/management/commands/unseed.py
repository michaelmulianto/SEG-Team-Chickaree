from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import User

class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.exclude(username = 'admin').delete()
