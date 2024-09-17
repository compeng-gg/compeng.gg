# Generated by Django 5.0.7 on 2024-09-17 12:46

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_accommodation'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='accommodation',
            unique_together={('user', 'assignment')},
        ),
    ]
