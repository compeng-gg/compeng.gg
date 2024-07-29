from django.core.management.base import BaseCommand, CommandError

from youtube_app.rest_api import YouTubeRestAPI
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "YouTube Test"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('YouTube Test'))
        user = User.objects.get(username=options['username'])
        api = YouTubeRestAPI(user)
        api.test()
