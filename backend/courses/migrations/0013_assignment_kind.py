# Generated by Django 5.0.7 on 2024-09-21 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0012_accommodation_max_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='kind',
            field=models.IntegerField(choices=[(1, 'Tests'), (2, 'Leaderboard')], default=1),
            preserve_default=False,
        ),
    ]