from django.core.management.base import BaseCommand, CommandError

from discord_app.rest_api import DiscordRestAPI

class Command(BaseCommand):
    help = "Discord Test"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Discord Test'))
        api = DiscordRestAPI()
        api.test()
