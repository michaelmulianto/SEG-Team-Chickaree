from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import User, Club

class Command(BaseCommand):
    """The database seeder."""
    PASSWORD = "Password123"
    USER_COUNT = 100
    CLUB_COUNT = 20

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        user_count = 0
        while user_count < Command.USER_COUNT:
            print(f'Seeding user {user_count}',  end='\r')
            try:
                self._create_user()
            except (django.db.utils.IntegrityError):
                continue
            user_count += 1
        print('User seeding complete')

        club_count = 0
        while club_count < Command.CLUB_COUNT:
            print(f'Seeding club {club_count}',  end='\r')
            try:
                self._create_club()
            except (django.db.utils.IntegrityError):
                continue
            club_count += 1
        print('Club seeding complete')

    def _create_club(self):
        name = self.faker.name()
        location = self.faker.country()
        description = self.faker.text(max_nb_chars=280)
        Club(
            name=name,
            location=location,
            description=description,
        )


    def _create_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._email(first_name, last_name)
        username = self._username(first_name, last_name)
        User.objects.create_user(
            username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=Command.PASSWORD,
        )

    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email

    def _username(self, first_name, last_name):
        username = f'@{first_name}{last_name}'
        return username
