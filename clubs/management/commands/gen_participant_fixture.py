"""This was used to help generate the large fixture file default_tournament_participants."""
from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import User, Club, Membership, Participant, Tournament

class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        c = Club.objects.create(
            id = 1,
            name = "King's Knights",
            location = "King's College London",
            description = "The best chess club in London.",
            created_on = "2021-11-20T03:04:05+00:00"
        )
        c.save()
        t = Tournament.objects.create(
            id = 1,
            club= c,
            name = "Grand Championship",
            description = "The most prestigious tournament in London.",
            capacity = 96,
            deadline="2023-12-9T00:00:00+00:00",
            start = "2023-12-10T00:00:00+00:00",
            end = "2023-12-20T00:00:00+00:00"
        )
        t.full_clean()
        t.save()
        for i in range(96):
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            email = f"{i}@example.org"
            username = f"User{i}"
            bio = ""

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

            member=Membership.objects.create(
                user=user,
                club=c,
            )    
            member.save()

            (Participant.objects.create(
                tournament=t,
                member=member
            )).save()
        