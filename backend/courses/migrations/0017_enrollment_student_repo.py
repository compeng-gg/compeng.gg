# Generated by Django 5.1.4 on 2025-01-02 21:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0016_offering_runner_repo'),
        ('github', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='student_repo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='enrollment_student', to='github.repository'),
        ),
    ]