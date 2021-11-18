from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import User, Club

class Command(BaseCommand):
    """The database seeder."""

    def handle(self, *args, **options):
        print("TODO: The databaseseeder will be added here...")
