# Generated by Django 5.0.1 on 2024-01-23 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Queued'), (2, 'In Progress'), (3, 'Success'), (4, 'Failure')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('data', models.JSONField(unique=True)),
                ('result', models.JSONField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
    ]
