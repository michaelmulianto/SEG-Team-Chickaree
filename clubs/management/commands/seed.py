from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from random import sample, choice
from clubs.models import User, Club, Member, Application

class Command(BaseCommand):
    """Fill the database with pseudorandom data"""
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
                bio = bio,
                experience = (i % 3) + 1,
                password = "Password123",
            )

            user.full_clean()
            user.save()

        for i in range(12):
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

            members = sample(list(User.objects.all()), (i%5)+6)
            
            Member.objects.create(
                club = club,
                user = members[0],
                is_owner = True,
            )

            for i in range(1,members.length-3):
                Member.objects.create(
                    club = club,
                    user = members[i],
                    is_officer = not(bool(i%4)),
                )

            for i in range(members.length-3,members.length):
                Application.objects.create(
                    club = club,
                    user = members[i],
                    personal_statement = self.faker.paragraph(nb_sentences=3),
                )
