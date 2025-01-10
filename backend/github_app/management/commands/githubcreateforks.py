from django.core.management.base import BaseCommand, CommandError

from github_app.utils import create_forks
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "GitHub Create Forks"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'Creating forks...'))
        for user in User.objects.all():
            create_forks(user)
