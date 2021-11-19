# Generated by Django 3.2.5 on 2021-11-18 14:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0005_member'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='description',
            field=models.CharField(max_length=280),
        ),
        migrations.AlterField(
            model_name='club',
            name='location',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='club',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
