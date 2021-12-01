from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import User, Club

class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        for i in range(100):
            first_name = self.faker.first_name()
            last_name = self.faker.unique.last_name()
            email = f"{first_name}.{last_name}@example.org"
            username = f"{first_name}{last_name}"
            bio = self.faker.paragraph(nb_sentences=3)

            user = User.objects.create_user(
                username = username,
                first_name = first_name,
                last_name = last_name,
                email = email,
                password = "Password123",
            )

            user.full_clean()
            user.save()

        for i in range(20):
            name = self.faker.unique.name()
            location = self.faker.country()
            description = self.faker.paragraph(nb_sentences=3)

            club = Club.objects.create(
                name = name,
                location = location,
                description = description
            )

            club.full_clean()
            club.save()
