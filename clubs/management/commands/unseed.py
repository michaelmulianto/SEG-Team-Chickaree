from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from microblogs.models import User, Club

class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        Club.objects.delete()
