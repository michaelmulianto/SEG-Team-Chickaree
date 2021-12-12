from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from random import sample, choice
from django.utils.timezone import now
from datetime import timedelta
from clubs.models import User, Club, Membership, Application, Ban, Tournament, Organiser, KnockoutStage, SingleGroup, Participant

class Command(BaseCommand):
    """Fill the database with pseudorandom data and some mandated test cases."""
    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def generate_random_data(self):
        for i in range(750):
            first_name = self.faker.first_name()
            while len(first_name) > 28:
                first_name = self.faker.first_name()

            last_name = self.faker.last_name()
            while len(last_name) > 28:
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

        for i in range(6):
            name = self.faker.unique.slug()
            while len(name) > 50:
                name = self.faker.unique.slug()

            location = self.faker.country()
            while len(location) > 50:
                location = self.faker.country()

            description = self.faker.paragraph(nb_sentences=3)

            club = Club.objects.create(
                name = name,
                location = location,
                description = description
            )
            club.full_clean()
            club.save()

            members = list(sample(list(User.objects.exclude(is_staff=True)), 125-(i%10)))

            owner = Membership.objects.create(
                club = club,
                user = members[0],
                is_owner = True,
            )

            owner.full_clean()
            owner.save()

            n = len(members)

            for j in range(1,n-15):
                m = Membership.objects.create(
                    club = club,
                    user = members[j],
                    is_officer = not(bool(i%10)),
                )
                m.full_clean()
                m.save()

            for j in range(n-15,n-5):
                a = Application.objects.create(
                    club = club,
                    user = members[j],
                    personal_statement = self.faker.paragraph(nb_sentences=3),
                )
                a.full_clean()
                a.save()

            for j in range(n-5,n):
                b = Ban.objects.create(
                    club = club,
                    user = members[j],
                )
                b.full_clean()
                b.save()

            # Generate 3 Tournaments, one complete, one partially complete, one not started.
            tournaments = []
            for j in range(0,3):
                if j == 0:
                    starttime = now() - timedelta(hours=48)
                elif j == 1:
                    starttime = now() - timedelta(hours=36)
                else:
                    starttime = now() + timedelta(hours=24)

                name = self.faker.unique.slug()
                while len(name) > 50:
                    name = self.faker.unique.slug()

                t = Tournament.objects.create(
                    club = club,
                    name = name,
                    description = self.faker.paragraph(nb_sentences=3),
                    capacity = 16 * (j+1),
                    start = starttime,
                    end = starttime + timedelta(hours=24),
                    deadline = starttime - timedelta(hours=24),
                )
                t.created_on = starttime - timedelta(hours=48)

                org_member = choice(list(Membership.objects.filter(club=club, is_officer=True)))
                o = Organiser.objects.create(
                    member = org_member,
                    tournament = t,
                    is_lead_organiser = True
                )
                o.full_clean()
                o.save()

                participants = list(sample(list(Membership.objects.exclude(id=org_member.id).filter(club=club)), t.capacity))
                for p in participants:
                    (Participant.objects.create(
                        member = p,
                        tournament = t
                    )).save()

                t.full_clean()
                t.save()
                tournaments.append(t)
            
            # Helper for tournament generation
            def complete_round(my_round):
                    # Arbitary result
                matches = my_round.get_matches()
                for match in matches:
                    match.result=1
                    match.black_player.round_eliminated = my_round.round_num
                    
            # Complete all rounds of first tournament
            tpast = tournaments[0]
            curr_round = tpast.generate_next_round()
            while not tpast.get_is_complete():
                complete_round(curr_round)
                curr_round = tpast.generate_next_round()
            
            # Complete 1 round of second tournament
            curr_round = tournaments[1].generate_next_round()
            complete_round(curr_round)
            tournaments[1].generate_next_round()

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

        jeb = User.objects.create_user(
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

        val = User.objects.create_user(
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

        billie = User.objects.create_user(
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
        m1 = Membership.objects.create(
            club = kerbal,
            user = jeb
        )
        m1.full_clean()
        m1.save()

        m2 = Membership.objects.create(
            club = kerbal,
            user = val,
            is_officer = True
        )
        m2.full_clean()
        m2.save()

        m3 = Membership.objects.create(
            club = kerbal,
            user = billie,
            is_owner = True
        )
        # Other memberships
        other_clubs = sample(list(Club.objects.exclude(id = kerbal.id)),3)

        jeb_officer = Membership.objects.create(
            club = other_clubs[0],
            user = jeb,
            is_officer = True
        )
        jeb_officer.full_clean()
        jeb_officer.save()

        # Here we delete the existing owner of the club that val will be the owner of.
        Membership.objects.filter(club=other_clubs[1],is_owner=True).delete()
        val_owner = Membership.objects.create(
            club = other_clubs[1],
            user = val,
            is_owner = True
        )
        val_owner.full_clean()
        val_owner.save()

        billie_member = Membership.objects.create(
            club = other_clubs[1],
            user = billie,
        )
        billie_member.full_clean()
        billie_member.save()

    def generate_edge_cases(self):
        """Generate data required to debug the user interface properly"""
        # Again this depends on data already existing.
        # Generates club with only an owner
        # Generates a club with an owner and 1 member

        # We hard code this so it can be logged in to.
        owner_user = User.objects.create_user(
            username = "testuser1",
            first_name = "Test",
            last_name = "Testson",
            email = "test@example.org",
            bio = "",
            experience = 1,
            password = "Password123",
        )
        owner_user.full_clean()
        owner_user.save()

        lonely_club = Club.objects.create(
            name="Lonely Chess Club",
            location="Some Dark Basement",
            description="Short desc."
        )
        lonely_club.full_clean()
        lonely_club.save()

        (Membership.objects.create(
            user = owner_user,
            club = lonely_club,
            is_owner = True
        )).save()

        less_lonely_club = Club.objects.create(
            name="Club 123",
            location="Aldwych",
            description="Very long desc: " + "x"*264
        )
        less_lonely_club.full_clean()
        less_lonely_club.save()

        (Membership.objects.create(
            user = owner_user,
            club = less_lonely_club,
            is_owner = True
        )).save()

        (Membership.objects.create(
            user = choice(list(User.objects.exclude(username="testuser1"))),
            club = less_lonely_club,
        )).save()

        (Ban.objects.create(
            user = choice(list(User.objects.exclude(username="testuser1"))),
            club = less_lonely_club,
        )).save()


    def handle(self, *args, **options):
        print("Seeding database... Please be patient...")
        # It is VERY important that random data is generated first, so we can fully control the memberships of the mandated users
        self.generate_random_data()
        self.generate_required_data()
        self.generate_edge_cases()
        print("Seeding Complete.")
