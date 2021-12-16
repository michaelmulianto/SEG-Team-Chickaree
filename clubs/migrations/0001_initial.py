# Generated by Django 3.2.5 on 2021-12-16 13:48

import clubs.models.validators
from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=32, unique=True, validators=[django.core.validators.RegexValidator(regex='^\\w{3,}$')])),
                ('last_name', models.CharField(max_length=48, validators=[django.core.validators.RegexValidator(regex="^[a-zA-Z\\'\\-]{1,}$")])),
                ('first_name', models.CharField(max_length=48, validators=[django.core.validators.RegexValidator(regex='^[a-zA-Z]{1,}$')])),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('bio', models.CharField(blank=True, default='', max_length=520)),
                ('experience', models.IntegerField(choices=[(1, 'Beginner'), (2, 'Intermediate'), (3, 'Advanced')], default=1)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('location', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=280)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_on'],
            },
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_officer', models.BooleanField(default=False)),
                ('is_owner', models.BooleanField(default=False)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['club'],
            },
        ),
        migrations.CreateModel(
            name='MemberTournamentRelationship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.membership')),
            ],
            options={
                'ordering': ['tournament'],
            },
        ),
        migrations.CreateModel(
            name='RoundOfMatches',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Organiser',
            fields=[
                ('membertournamentrelationship_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='clubs.membertournamentrelationship')),
                ('is_lead_organiser', models.BooleanField(default=False)),
            ],
            bases=('clubs.membertournamentrelationship',),
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('membertournamentrelationship_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='clubs.membertournamentrelationship')),
                ('round_eliminated', models.IntegerField(default=-1)),
                ('joined', models.DateTimeField(auto_now_add=True)),
            ],
            bases=('clubs.membertournamentrelationship',),
        ),
        migrations.CreateModel(
            name='SingleGroup',
            fields=[
                ('roundofmatches_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='clubs.roundofmatches')),
                ('winners_required', models.IntegerField(default=1)),
            ],
            options={
                'abstract': False,
            },
            bases=('clubs.roundofmatches', models.Model),
        ),
        migrations.CreateModel(
            name='TournamentStageBase',
            fields=[
                ('roundofmatches_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='clubs.roundofmatches')),
                ('round_num', models.IntegerField(default=1)),
            ],
            options={
                'ordering': ['tournament'],
            },
            bases=('clubs.roundofmatches',),
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=280)),
                ('capacity', models.PositiveIntegerField(default=16, validators=[django.core.validators.MinValueValidator(2), django.core.validators.MaxValueValidator(96), clubs.models.validators.ValueInListValidator((2, 4, 8, 16, 32, 48, 96))])),
                ('deadline', models.DateTimeField()),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club')),
            ],
            options={
                'ordering': ['start'],
            },
        ),
        migrations.AddField(
            model_name='roundofmatches',
            name='tournament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournament', to='clubs.tournament'),
        ),
        migrations.AddField(
            model_name='membertournamentrelationship',
            name='tournament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.tournament'),
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.IntegerField(choices=[(0, 'Incomplete'), (1, 'White Victory'), (2, 'Black Victory'), (3, 'Stalemate')], default=0)),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.roundofmatches')),
            ],
            options={
                'ordering': ['collection'],
            },
        ),
        migrations.CreateModel(
            name='Ban',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['club'],
            },
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('personal_statement', models.CharField(default='', max_length=580)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['club'],
            },
        ),
        migrations.CreateModel(
            name='GroupStage',
            fields=[
                ('tournamentstagebase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='clubs.tournamentstagebase')),
            ],
            options={
                'abstract': False,
            },
            bases=('clubs.tournamentstagebase', models.Model),
        ),
        migrations.CreateModel(
            name='KnockoutStage',
            fields=[
                ('tournamentstagebase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='clubs.tournamentstagebase')),
            ],
            options={
                'abstract': False,
            },
            bases=('clubs.tournamentstagebase', models.Model),
        ),
        migrations.AddConstraint(
            model_name='tournament',
            constraint=models.UniqueConstraint(fields=('club', 'name'), name='tournament_name_must_be_unique_by_club'),
        ),
        migrations.AddConstraint(
            model_name='membertournamentrelationship',
            constraint=models.UniqueConstraint(fields=('member', 'tournament'), name='one_object_per_relationship'),
        ),
        migrations.AddConstraint(
            model_name='membership',
            constraint=models.UniqueConstraint(fields=('club', 'user'), name='user_in_club_unique'),
        ),
        migrations.AddField(
            model_name='match',
            name='black_player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='black', to='clubs.participant'),
        ),
        migrations.AddField(
            model_name='match',
            name='white_player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='white', to='clubs.participant'),
        ),
        migrations.AddConstraint(
            model_name='ban',
            constraint=models.UniqueConstraint(fields=('club', 'user'), name='user_ban_from_club_unique'),
        ),
        migrations.AddConstraint(
            model_name='application',
            constraint=models.UniqueConstraint(fields=('club', 'user'), name='application_to_club_unique'),
        ),
        migrations.AddField(
            model_name='singlegroup',
            name='group_stage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.groupstage'),
        ),
        migrations.AddConstraint(
            model_name='match',
            constraint=models.CheckConstraint(check=models.Q(('white_player', django.db.models.expressions.F('black_player')), _negated=True), name='cannot_play_self'),
        ),
    ]
