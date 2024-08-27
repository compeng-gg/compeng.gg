# Generated by Django 5.0.7 on 2024-08-27 16:12

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_rename_discord_role_id_institution_verified_discord_role_id_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together={('user', 'role')},
        ),
    ]
