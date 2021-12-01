from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from random import sample, choice
from clubs.models import User, Club, Member, Application

class Command(BaseCommand):
    """Fill the database with pseudorandom data"""
    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def generate_random_data(self):
        for i in range(100):
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            email = f"{first_name}.{last_name}{i}@example.org"
            username = f"{first_name}{i}"
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
            name = self.faker.unique.company()
            location = self.faker.country()
            description = self.faker.paragraph(nb_sentences=3)

            club = Club.objects.create(
                name = name,
                location = location,
                description = description
            )
            club.full_clean()
            club.save()

            members = sample(list(User.objects.exclude(is_staff=True)), (i%5)+6)
            
            owner = Member.objects.create(
                club = club,
                user = members[0],
                is_owner = True,
            )

            owner.full_clean()
            owner.save()

            for i in range(1,len(members)-3):
                m = Member.objects.create(
                    club = club,
                    user = members[i],
                    is_officer = not(bool(i%4)),
                )
                m.full_clean()
                m.save()

            for i in range(len(members)-3,len(members)):
                a = Application.objects.create(
                    club = club,
                    user = members[i],
                    personal_statement = self.faker.paragraph(nb_sentences=3),
                )
                a.full_clean()
                a.save()

    def generate_required_data(self):
        """This is the data needed as part of non-functional requirements"""

        # 3 Users jeb val and billie
        # All to be members of one club "kerbal chess club"
        # Billie is owner, val officer and jeb member
        # They should all also be part of at least 1 other club each
        # As member, owner and officer respective to billie, val and jeb

        kerbal = Club.objects.create(
            name="Kerbal Chess Club",
            location="Bush House Auditorium",
            description="Jeroen's Favourite Club."
        )
        kerbal.full_clean()
        kerbal.save()

        jeb = User.objects.create(
            username = "Jebediah142",
            first_name = "Jebediah",
            last_name = "Kerman",
            email = "jeb@example.org",
            bio = "",
            experience = 1,
            password = "Password123"
        )
        jeb.full_clean()
        jeb.save()

        val = User.objects.create(
            username = "Valentina123",
            first_name = "Valentina",
            last_name = "Kerman",
            email = "val@example.org",
            bio = "",
            experience = 2,
            password = "Password123"
        )
        val.full_clean()
        val.save()

        billie = User.objects.create(
            username = "Billie444",
            first_name = "Billie",
            last_name = "Kerman",
            email = "billie@example.org",
            bio = "",
            experience = 3,
            password = "Password123"
        )
        billie.full_clean()
        billie.save()

        # Memberships to Kerbal
        m1 = Member.objects.create(
            club = kerbal,
            user = jeb
        )
        m1.full_clean()
        m1.save()

        m2 = Member.objects.create(
            club = kerbal,
            user = val,
            is_officer = True
        )
        m2.full_clean()
        m2.save()

        m3 = Member.objects.create(
            club = kerbal,
            user = billie,
            is_owner = True
        )
        # Other memberships
        other_clubs = sample(list(Club.objects.exclude(id = kerbal.id)),3)

        jeb_officer = Member.objects.create(
            club = other_clubs[0],
            user = jeb,
            is_officer = True
        )
        jeb_officer.full_clean()
        jeb_officer.save()

        # Here we delete the existing owner of the club that val will be the owner of.
        Member.objects.filter(club=other_clubs[1],is_owner=True).delete()
        val_owner = Member.objects.create(
            club = other_clubs[1],
            user = val,
            is_owner = True
        )
        val_owner.full_clean()
        val_owner.save()

        billie_member = Member.objects.create(
            club = other_clubs[1],
            user = billie,
        )
        billie_member.full_clean()
        billie_member.save()

    def handle(self, *args, **options):
        # It is VERY important that random data is generated first, so we can fully control the memberships of the mandated users
        self.generate_random_data()
        self.generate_required_data()
