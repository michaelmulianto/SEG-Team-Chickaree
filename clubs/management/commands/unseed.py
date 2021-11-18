from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import User, Club

class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.exclude(username = 'admin').delete()
        Club.objects.delete()
