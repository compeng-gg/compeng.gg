# Generated by Django 5.0.7 on 2024-09-13 14:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_assignment_assignmenttask'),
        ('runner', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='assignmenttask',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='runner.task'),
        ),
        migrations.AddField(
            model_name='assignmenttask',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
