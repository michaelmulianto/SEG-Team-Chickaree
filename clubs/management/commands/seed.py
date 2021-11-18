from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from ..clubs.models import User

class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        for i in range(100):
            fn = self.faker.unique.first_name()
            ln = self.faker.unique.last_name()
            e = f"{fn}.{ln}@example.org"
            us = f"@{fn}{ln}"

            user = User.objects.create_user(
                username = us,
                first_name = fn,
                last_name = ln,
                email = e,
                password = "Password123",
            )

            user.full_clean()
            user.save()
